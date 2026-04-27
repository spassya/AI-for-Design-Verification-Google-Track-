
module tb;

  reg clk;
  reg rst;
  reg push_valid;
  reg [7:0] push_data;
  reg pop_ready;

  wire push_ready;
  wire pop_valid;
  wire [7:0] pop_data;
  wire full;
  wire empty;
  wire [3:0] items;
  wire [3:0] slots;
  wire full_next;
  wire empty_next;
  wire [3:0] items_next;
  wire [3:0] slots_next;

  integer errors;
  integer i;

  fifo_flops dut (
    .clk(clk),
    .rst(rst),
    .push_valid(push_valid),
    .push_ready(push_ready),
    .push_data(push_data),
    .pop_ready(pop_ready),
    .pop_valid(pop_valid),
    .pop_data(pop_data),
    .full(full),
    .empty(empty),
    .items(items),
    .slots(slots),
    .full_next(full_next),
    .empty_next(empty_next),
    .items_next(items_next),
    .slots_next(slots_next)
  );

  always #5 clk = ~clk;

  task reset_fifo;
    begin
      rst = 1;
      push_valid = 0;
      pop_ready = 0;
      push_data = 0;
      @(posedge clk);
      #2;
      rst = 0;
      #2;

      if (empty !== 1 || full !== 0 || push_ready !== 1 || pop_valid !== 0) begin
        $display("FAIL reset state");
        errors = errors + 1;
      end
    end
  endtask

  task push_one;
    input [7:0] data;
    begin
      push_valid = 1;
      push_data = data;
      pop_ready = 0;
      @(posedge clk);
      #2;
      push_valid = 0;
    end
  endtask

  task pop_expect;
    input [7:0] data;
    begin
      #2;
      if (pop_valid !== 1) begin
        $display("FAIL pop_valid expected 1");
        errors = errors + 1;
      end

      if (pop_data !== data) begin
        $display("FAIL pop_data expected=%h got=%h", data, pop_data);
        errors = errors + 1;
      end

      pop_ready = 1;
      @(posedge clk);
      #2;
      pop_ready = 0;
    end
  endtask

  task check_bypass;
    input [7:0] data;
    begin
      push_valid = 1;
      push_data = data;
      pop_ready = 1;
      #2;

      if (pop_valid !== 1 || pop_data !== data) begin
        $display("FAIL bypass");
        errors = errors + 1;
      end

      @(posedge clk);
      #2;
      push_valid = 0;
      pop_ready = 0;
    end
  endtask

  initial begin
    clk = 0;
    errors = 0;

    reset_fifo();

    // Bypass
    check_bypass(8'hA5);

    // Basic FIFO order
    push_one(8'h11);
    push_one(8'h22);
    pop_expect(8'h11);
    pop_expect(8'h22);

    // Stronger checks
    reset_fifo();

    push_one(8'hA1);
    #2;
    if (empty !== 0 || pop_valid !== 1 || items !== 1 || slots !== 12) begin
      $display("FAIL after 1 push");
      errors = errors + 1;
    end

    push_one(8'hB2);
    #2;
    if (items !== 2 || slots !== 11) begin
      $display("FAIL after 2 pushes");
      errors = errors + 1;
    end

    pop_expect(8'hA1);
    #2;
    if (items !== 1 || slots !== 12) begin
      $display("FAIL after 1 pop");
      errors = errors + 1;
    end

    pop_expect(8'hB2);
    #2;
    if (empty !== 1 || pop_valid !== 0 || items !== 0 || slots !== 13) begin
      $display("FAIL after drain");
      errors = errors + 1;
    end

    // Full test
    reset_fifo();

    for (i = 0; i < 13; i = i + 1)
      push_one(i);

    #2;
    if (full !== 1 || push_ready !== 0 || items !== 13 || slots !== 0) begin
      $display("FAIL full state");
      errors = errors + 1;
    end

    // Push when full
    push_valid = 1;
    push_data = 8'hFF;
    @(posedge clk);
    #2;
    push_valid = 0;

    if (items !== 13) begin
      $display("FAIL push when full changed state");
      errors = errors + 1;
    end

    for (i = 0; i < 13; i = i + 1)
      pop_expect(i);

    #2;
    if (empty !== 1 || items !== 0) begin
      $display("FAIL final empty");
      errors = errors + 1;
    end

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
