
module tb;

  reg clk;
  reg rst;
  reg reinit;
  reg advance;
  reg [4:0] initial_state;
  reg [4:0] taps;
  wire [4:0] out_state;
  wire out;

  integer errors;
  integer i;
  reg [4:0] expected_state;
  reg feedback;

  lfsr dut (
    .clk(clk),
    .rst(rst),
    .reinit(reinit),
    .advance(advance),
    .initial_state(initial_state),
    .taps(taps),
    .out_state(out_state),
    .out(out)
  );

  always #5 clk = ~clk;

  task check_outputs;
    begin
      #1;
      if (out_state !== expected_state) begin
        $display("FAIL out_state expected=%b got=%b", expected_state, out_state);
        errors = errors + 1;
      end

      if (out !== expected_state[0]) begin
        $display("FAIL out expected=%b got=%b", expected_state[0], out);
        errors = errors + 1;
      end
    end
  endtask

  task do_reset;
    input [4:0] t_initial;
    input [4:0] t_taps;
    begin
      initial_state = t_initial;
      taps = t_taps;
      rst = 1'b1;
      reinit = 1'b0;
      advance = 1'b0;

      @(posedge clk);
      expected_state = t_initial;
      check_outputs();

      rst = 1'b0;
    end
  endtask

  task do_reinit;
    input [4:0] t_initial;
    begin
      initial_state = t_initial;
      reinit = 1'b1;
      advance = 1'b1;

      @(posedge clk);
      expected_state = t_initial;
      check_outputs();

      reinit = 1'b0;
      advance = 1'b0;
    end
  endtask

  task do_advance;
    begin
      rst = 1'b0;
      reinit = 1'b0;
      advance = 1'b1;

      feedback = ^(expected_state & taps);
      expected_state = {expected_state[3:0], feedback};

      @(posedge clk);
      check_outputs();

      advance = 1'b0;
    end
  endtask

  task do_hold;
    begin
      rst = 1'b0;
      reinit = 1'b0;
      advance = 1'b0;

      @(posedge clk);
      check_outputs();
    end
  endtask

  initial begin
    clk = 0;
    rst = 0;
    reinit = 0;
    advance = 0;
    initial_state = 0;
    taps = 0;
    expected_state = 0;
    errors = 0;

    // Basic reset and hold
    do_reset(5'b10101, 5'b10010);
    do_hold();
    do_hold();

    // Advance sequence
    for (i = 0; i < 10; i = i + 1)
      do_advance();

    // Reinit must override advance
    do_reinit(5'b01101);
    do_hold();

    // Different taps
    do_reset(5'b11111, 5'b10101);
    for (i = 0; i < 12; i = i + 1)
      do_advance();

    // Edge cases
    do_reset(5'b00001, 5'b11111);
    for (i = 0; i < 8; i = i + 1)
      do_advance();

    do_reset(5'b10000, 5'b00001);
    for (i = 0; i < 8; i = i + 1)
      do_advance();

    do_reset(5'b01010, 5'b01010);
    for (i = 0; i < 8; i = i + 1)
      do_advance();

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
