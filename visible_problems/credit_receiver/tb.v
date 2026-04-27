
module tb;

  reg clk;
  reg rst;
  reg push_valid;
  reg [7:0] push_data;
  reg push_sender_in_reset;
  reg push_credit_stall;
  reg credit_initial;
  reg credit_withhold;
  reg pop_credit;

  wire pop_valid;
  wire [7:0] pop_data;
  wire push_credit;
  wire push_receiver_in_reset;
  wire credit_available;
  wire credit_count;

  integer errors;

  credit_receiver dut (
    .clk(clk),
    .rst(rst),
    .push_valid(push_valid),
    .push_data(push_data),
    .pop_valid(pop_valid),
    .pop_data(pop_data),
    .push_sender_in_reset(push_sender_in_reset),
    .push_receiver_in_reset(push_receiver_in_reset),
    .push_credit_stall(push_credit_stall),
    .push_credit(push_credit),
    .credit_initial(credit_initial),
    .credit_withhold(credit_withhold),
    .credit_available(credit_available),
    .credit_count(credit_count),
    .pop_credit(pop_credit)
  );

  always #5 clk = ~clk;

  task reset_with;
    input init_credit;
    begin
      rst = 1'b1;
      push_sender_in_reset = 1'b0;
      push_valid = 1'b0;
      push_data = 8'h00;
      push_credit_stall = 1'b0;
      credit_initial = init_credit;
      credit_withhold = 1'b0;
      pop_credit = 1'b0;

      @(posedge clk);
      #2;

      rst = 1'b0;
      #2;
    end
  endtask

  task check_data_path;
    input [7:0] data;
    begin
      push_data = data;
      push_valid = 1'b1;
      push_sender_in_reset = 1'b0;
      rst = 1'b0;
      #2;

      if (pop_data !== data) begin
        $display("FAIL pop_data expected=%h got=%h", data, pop_data);
        errors = errors + 1;
      end

      if (pop_valid !== 1'b1) begin
        $display("FAIL pop_valid should follow push_valid when not reset");
        errors = errors + 1;
      end

      push_valid = 1'b0;
      #2;

      if (pop_valid !== 1'b0) begin
        $display("FAIL pop_valid should be 0 when push_valid is 0");
        errors = errors + 1;
      end
    end
  endtask

  task check_reset_blocks;
    begin
      push_valid = 1'b1;
      push_data = 8'hAA;

      rst = 1'b1;
      push_sender_in_reset = 1'b0;
      #2;
      if (pop_valid !== 1'b0) begin
        $display("FAIL rst should block pop_valid");
        errors = errors + 1;
      end

      if (push_receiver_in_reset !== 1'b1) begin
        $display("FAIL push_receiver_in_reset should equal rst");
        errors = errors + 1;
      end

      rst = 1'b0;
      push_sender_in_reset = 1'b1;
      #2;
      if (pop_valid !== 1'b0) begin
        $display("FAIL push_sender_in_reset should block pop_valid");
        errors = errors + 1;
      end

      push_sender_in_reset = 1'b0;
      push_valid = 1'b0;
      #2;
    end
  endtask

  task check_credit_basic;
    begin
      reset_with(1'b1);

      push_credit_stall = 1'b0;
      credit_withhold = 1'b0;
      push_sender_in_reset = 1'b0;
      rst = 1'b0;
      #2;

      if (credit_count !== 1'b1) begin
        $display("FAIL credit_count should initialize to 1");
        errors = errors + 1;
      end

      if (credit_available !== 1'b1) begin
        $display("FAIL credit_available should be 1");
        errors = errors + 1;
      end

      if (push_credit !== 1'b1) begin
        $display("FAIL push_credit should assert when credit available");
        errors = errors + 1;
      end

      push_credit_stall = 1'b1;
      #2;
      if (push_credit !== 1'b0) begin
        $display("FAIL push_credit_stall should block push_credit");
        errors = errors + 1;
      end

      push_credit_stall = 1'b0;
      credit_withhold = 1'b1;
      #2;

      if (credit_available !== 1'b0) begin
        $display("FAIL credit_withhold should make credit_available 0");
        errors = errors + 1;
      end

      if (push_credit !== 1'b0) begin
        $display("FAIL withheld credit should block push_credit");
        errors = errors + 1;
      end
    end
  endtask

  task check_credit_decrement_increment;
    begin
      reset_with(1'b1);

      push_credit_stall = 1'b0;
      credit_withhold = 1'b0;
      push_sender_in_reset = 1'b0;
      pop_credit = 1'b0;
      #2;

      if (push_credit !== 1'b1) begin
        $display("FAIL expected push_credit before decrement");
        errors = errors + 1;
      end

      // push_credit sent, so next cycle credit_count should decrement to 0
      @(posedge clk);
      #2;

      if (credit_count !== 1'b0) begin
        $display("FAIL credit_count should decrement to 0 after push_credit");
        errors = errors + 1;
      end

      if (push_credit !== 1'b0) begin
        $display("FAIL push_credit should stop when credit_count is 0");
        errors = errors + 1;
      end

      // pop_credit returns credit, so count should increment to 1
      pop_credit = 1'b1;
      @(posedge clk);
      #2;
      pop_credit = 1'b0;
      #2;

      if (credit_count !== 1'b1) begin
        $display("FAIL credit_count should increment to 1 after pop_credit");
        errors = errors + 1;
      end

      if (push_credit !== 1'b1) begin
        $display("FAIL push_credit should reassert after credit returns");
        errors = errors + 1;
      end

      // Simultaneous pop_credit and push_credit should keep count stable
      pop_credit = 1'b1;
      @(posedge clk);
      #2;
      pop_credit = 1'b0;
      #2;

      if (credit_count !== 1'b1) begin
        $display("FAIL simultaneous credit in/out should keep count at 1");
        errors = errors + 1;
      end
    end
  endtask

  initial begin
    clk = 0;
    rst = 0;
    push_valid = 0;
    push_data = 0;
    push_sender_in_reset = 0;
    push_credit_stall = 0;
    credit_initial = 0;
    credit_withhold = 0;
    pop_credit = 0;
    errors = 0;

    reset_with(1'b0);
    check_data_path(8'hA5);
    check_data_path(8'h3C);
    // Targeted test: pop_data must exactly equal push_data
   // This eliminates the mutant that changes pop_data[0]
    check_data_path(8'h00);

    check_reset_blocks();

    check_credit_basic();
    // Targeted reset initialization check with credit_initial = 0
    reset_with(1'b0);
    #2;

    if (credit_count !== 1'b0) begin
      $display("FAIL credit_count should initialize to 0");
      errors = errors + 1;
    end

    if (credit_available !== 1'b0) begin
      $display("FAIL credit_available should be 0 when credit_count is 0");
      errors = errors + 1;
    end

    if (push_credit !== 1'b0) begin
      $display("FAIL push_credit should be 0 when no credit is available");
      errors = errors + 1;
    end
    

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
