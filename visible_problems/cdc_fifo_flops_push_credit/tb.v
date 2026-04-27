
module tb;

  reg push_clk, pop_clk;
  reg push_rst, pop_rst;
  reg push_sender_in_reset;
  reg push_valid;
  reg [7:0] push_data;
  reg push_credit_stall;
  reg pop_ready;
  reg [4:0] credit_initial_push;
  reg [4:0] credit_withhold_push;

  wire push_receiver_in_reset;
  wire push_credit;
  wire push_full;
  wire [4:0] push_slots;
  wire [4:0] credit_count_push;
  wire [4:0] credit_available_push;
  wire pop_valid;
  wire [7:0] pop_data;
  wire pop_empty;
  wire [4:0] pop_items;

  integer errors;
  integer i;

  cdc_fifo_flops_push_credit dut (
    .push_clk(push_clk),
    .pop_clk(pop_clk),
    .push_rst(push_rst),
    .pop_rst(pop_rst),
    .push_sender_in_reset(push_sender_in_reset),
    .push_receiver_in_reset(push_receiver_in_reset),
    .push_valid(push_valid),
    .push_data(push_data),
    .push_credit_stall(push_credit_stall),
    .push_credit(push_credit),
    .push_full(push_full),
    .push_slots(push_slots),
    .credit_initial_push(credit_initial_push),
    .credit_withhold_push(credit_withhold_push),
    .credit_count_push(credit_count_push),
    .credit_available_push(credit_available_push),
    .pop_ready(pop_ready),
    .pop_valid(pop_valid),
    .pop_data(pop_data),
    .pop_empty(pop_empty),
    .pop_items(pop_items)
  );

  always #2 push_clk = ~push_clk;
  always #3 pop_clk = ~pop_clk;

  task reset_fifo;
    begin
      push_rst = 1'b1;
      pop_rst = 1'b1;
      push_sender_in_reset = 1'b0;
      push_valid = 1'b0;
      push_data = 8'h00;
      push_credit_stall = 1'b0;
      pop_ready = 1'b0;
      credit_initial_push = 5'd17;
      credit_withhold_push = 5'd0;

      repeat (2) @(posedge push_clk);
      repeat (2) @(posedge pop_clk);

      push_rst = 1'b0;
      pop_rst = 1'b0;

      repeat (2) @(posedge push_clk);
      repeat (2) @(posedge pop_clk);
      #1;
    end
  endtask

  task push_one;
    input [7:0] data;
    begin
      push_data = data;
      push_valid = 1'b1;
      @(posedge push_clk);
      #1;
      push_valid = 1'b0;
      #1;
    end
  endtask

  task pop_one_expect;
    input [7:0] data;
    begin
      repeat (4) @(posedge pop_clk);
      #1;

      if (pop_valid !== 1'b1) begin
        $display("FAIL pop_valid expected 1");
        errors = errors + 1;
      end

      if (pop_data !== data) begin
        $display("FAIL pop_data expected=%h got=%h", data, pop_data);
        errors = errors + 1;
      end

      pop_ready = 1'b1;
      @(posedge pop_clk);
      #1;
      pop_ready = 1'b0;
      #1;
    end
  endtask

  task hold_expect;
    input [7:0] data;
    begin
      repeat (4) @(posedge pop_clk);
      #1;

      if (pop_valid !== 1'b1 || pop_data !== data) begin
        $display("FAIL hold setup expected=%h got valid=%b data=%h",
                 data, pop_valid, pop_data);
        errors = errors + 1;
      end

      pop_ready = 1'b0;
      repeat (3) @(posedge pop_clk);
      #1;

      if (pop_valid !== 1'b1 || pop_data !== data) begin
        $display("FAIL data not held when pop_ready=0");
        errors = errors + 1;
      end
    end
  endtask

  task status_credit_probe;
    integer cyc;
    reg [31:0] lfsr;
    begin
      lfsr = 32'h1ACE_B00C;
      push_rst = 1'b1;
      pop_rst = 1'b1;
      push_sender_in_reset = 1'b0;
      push_valid = 1'b0;
      push_data = 8'h00;
      push_credit_stall = 1'b0;
      pop_ready = 1'b0;
      credit_initial_push = 5'd17;
      credit_withhold_push = 5'd0;

      for (cyc = 0; cyc < 12; cyc = cyc + 1) begin
        @(negedge push_clk);
        lfsr = {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};
        push_rst = (cyc < 4);
        pop_rst = (cyc < 5);
        @(posedge push_clk);
        #1;
      end

      for (cyc = 12; cyc < 70; cyc = cyc + 1) begin
        @(negedge push_clk);
        lfsr = {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};
        push_rst = 1'b0;
        pop_rst = 1'b0;
        push_sender_in_reset = (cyc > 40 && cyc < 45);
        push_credit_stall = lfsr[3] & ~lfsr[7];
        push_valid = (lfsr[0] ^ lfsr[5]) & ~push_sender_in_reset;
        push_data = lfsr[15:8] ^ cyc[7:0];
        pop_ready = lfsr[2] | lfsr[9];
        case (cyc[5:3])
          0: begin credit_initial_push = 5'd17; credit_withhold_push = 5'd0; end
          1: begin credit_initial_push = 5'd9; credit_withhold_push = 5'd2; end
          2: begin credit_initial_push = 5'd5; credit_withhold_push = 5'd4; end
          3: begin credit_initial_push = 5'd1; credit_withhold_push = 5'd0; end
          default: begin credit_initial_push = 5'd13; credit_withhold_push = 5'd1; end
        endcase
        @(posedge push_clk);
        #1;

        if (cyc == 27 && push_slots !== 5'd12) begin
          $display("FAIL push_slots cycle 27 expected 12 got=%0d", push_slots);
          errors = errors + 1;
        end

        if (cyc == 43) begin
          if (push_full !== 1'b0) begin
            $display("FAIL push_full cycle 43 expected 0 got=%b", push_full);
            errors = errors + 1;
          end
          if (push_slots !== 5'd26) begin
            $display("FAIL push_slots cycle 43 expected 26 got=%0d", push_slots);
            errors = errors + 1;
          end
        end

        if (cyc == 61 && push_slots !== 5'd27) begin
          $display("FAIL push_slots cycle 61 expected 27 got=%0d", push_slots);
          errors = errors + 1;
        end
      end

      push_valid = 1'b0;
      pop_ready = 1'b0;
      push_sender_in_reset = 1'b0;
      push_credit_stall = 1'b0;
    end
  endtask

  initial begin
    push_clk = 0;
    pop_clk = 0;
    push_rst = 0;
    pop_rst = 0;
    push_sender_in_reset = 0;
    push_valid = 0;
    push_data = 0;
    push_credit_stall = 0;
    pop_ready = 0;
    credit_initial_push = 5'd17;
    credit_withhold_push = 5'd0;
    errors = 0;

    status_credit_probe();

    reset_fifo();

    if (push_full !== 1'b0) begin
      $display("FAIL push_full should be 0 after reset");
      errors = errors + 1;
    end

    if (pop_empty !== 1'b1) begin
      $display("FAIL pop_empty should be 1 after reset");
      errors = errors + 1;
    end

    if (push_slots !== 5'd17) begin
      $display("FAIL push_slots should be 17 after reset, got=%0d", push_slots);
      errors = errors + 1;
    end

    push_one(8'hA5);
    push_one(8'h11);
    push_one(8'h22);

    repeat (4) @(posedge pop_clk);
    #1;

    if (pop_empty !== 1'b0) begin
      $display("FAIL pop_empty should be 0 after pushes");
      errors = errors + 1;
    end

    if (pop_items < 5'd1) begin
      $display("FAIL pop_items should show data after pushes, got=%0d", pop_items);
      errors = errors + 1;
    end

    pop_one_expect(8'hA5);
    pop_one_expect(8'h11);
    pop_one_expect(8'h22);

    // Empty check after all items popped
    repeat (4) @(posedge pop_clk);
    #1;

    if (pop_valid !== 1'b0) begin
      $display("FAIL pop_valid should be 0 after FIFO is drained");
      errors = errors + 1;
    end

    if (pop_empty !== 1'b1) begin
      $display("FAIL pop_empty should be 1 after FIFO is drained");
      errors = errors + 1;
    end

    push_one(8'hCC);
    hold_expect(8'hCC);
    pop_one_expect(8'hCC);

    // Deep FIFO storage test 1
    reset_fifo();

    for (i = 0; i < 11; i = i + 1) begin
      if (i == 10)
        push_one(8'h08);
      else
        push_one(i[7:0]);
    end

    for (i = 0; i < 10; i = i + 1)
      pop_one_expect(i[7:0]);

    pop_one_expect(8'h08);

    // Deep FIFO storage test 2
    reset_fifo();

    for (i = 0; i < 12; i = i + 1) begin
      if (i == 11)
        push_one(8'h80);
      else
        push_one(i[7:0] + 8'h20);
    end

    for (i = 0; i < 11; i = i + 1)
      pop_one_expect(i[7:0] + 8'h20);

    pop_one_expect(8'h80);

    // Deep FIFO storage test 3
    reset_fifo();

    for (i = 0; i < 13; i = i + 1) begin
      if (i == 12)
        push_one(8'h40);
      else
        push_one(i[7:0] + 8'h30);
    end

    for (i = 0; i < 12; i = i + 1)
      pop_one_expect(i[7:0] + 8'h30);

    pop_one_expect(8'h40);

    // Deep FIFO storage test 4
    reset_fifo();

    for (i = 0; i < 15; i = i + 1) begin
      if (i == 14)
        push_one(8'h24);
      else
        push_one(i[7:0] + 8'h40);
    end

    for (i = 0; i < 14; i = i + 1)
      pop_one_expect(i[7:0] + 8'h40);

    pop_one_expect(8'h24);

    // Deep FIFO stress test
    reset_fifo();

    for (i = 0; i < 17; i = i + 1) begin
      case (i)
        13: push_one(8'h3C);
        14: push_one(8'h5A);
        15: push_one(8'hA6);
        16: push_one(8'hC9);
        default: push_one(i[7:0] + 8'h60);
      endcase
    end

    for (i = 0; i < 17; i = i + 1) begin
      case (i)
        13: pop_one_expect(8'h3C);
        14: pop_one_expect(8'h5A);
        15: pop_one_expect(8'hA6);
        16: pop_one_expect(8'hC9);
        default: pop_one_expect(i[7:0] + 8'h60);
      endcase
    end
    
             
    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
