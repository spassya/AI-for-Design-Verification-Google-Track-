
module tb;

  reg clk;
  reg rst;
  reg reinit;
  reg incr_valid;
  reg decr_valid;
  reg [3:0] initial_value;
  reg [1:0] incr;
  reg [1:0] decr;
  wire [3:0] value;
  wire [3:0] value_next;

  integer errors;
  integer expected_value;
  integer expected_next;

  counter dut (
    .clk(clk),
    .rst(rst),
    .reinit(reinit),
    .incr_valid(incr_valid),
    .decr_valid(decr_valid),
    .initial_value(initial_value),
    .incr(incr),
    .decr(decr),
    .value(value),
    .value_next(value_next)
  );

  always #5 clk = ~clk;

  function integer wrap_0_10;
    input integer x;
    begin
      while (x < 0)
        x = x + 11;
      while (x > 10)
        x = x - 11;
      wrap_0_10 = x;
    end
  endfunction

  task apply_and_check;
    input reg t_rst;
    input reg t_reinit;
    input reg t_incr_valid;
    input reg t_decr_valid;
    input reg [3:0] t_initial_value;
    input reg [1:0] t_incr;
    input reg [1:0] t_decr;
    input reg check_value_next_now;
    begin
      rst = t_rst;
      reinit = t_reinit;
      incr_valid = t_incr_valid;
      decr_valid = t_decr_valid;
      initial_value = t_initial_value;
      incr = t_incr;
      decr = t_decr;

      if (t_rst) begin
        expected_next = t_initial_value;
      end else if (t_reinit) begin
        expected_next = t_initial_value;
      end else begin
        expected_next = expected_value;
        if (t_incr_valid)
          expected_next = expected_next + t_incr;
        if (t_decr_valid)
          expected_next = expected_next - t_decr;
        expected_next = wrap_0_10(expected_next);
      end

      #1;
      if (check_value_next_now && (value_next !== expected_next[3:0])) begin
        $display("FAIL value_next mismatch: rst=%0d reinit=%0d incr_valid=%0d decr_valid=%0d expected=%0d got=%0d",
                 t_rst, t_reinit, t_incr_valid, t_decr_valid, expected_next, value_next);
        errors = errors + 1;
      end

      @(posedge clk);
      #1;
      expected_value = expected_next;

      if (value !== expected_value[3:0]) begin
        $display("FAIL value mismatch after clock: rst=%0d reinit=%0d incr_valid=%0d decr_valid=%0d expected=%0d got=%0d",
                 t_rst, t_reinit, t_incr_valid, t_decr_valid, expected_value, value);
        errors = errors + 1;
      end
    end
  endtask

  integer initv;
  integer a;
  integer b;

  initial begin
    clk = 0;
    rst = 0;
    reinit = 0;
    incr_valid = 0;
    decr_valid = 0;
    initial_value = 0;
    incr = 0;
    decr = 0;
    errors = 0;
    expected_value = 0;
    expected_next = 0;

    // Bring DUT into a known state first.
    apply_and_check(1'b1, 1'b0, 1'b0, 1'b0, 4'd5, 2'd0, 2'd0, 1'b0);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b0, 4'd5, 2'd0, 2'd0, 1'b1);

    // Reinit overrides incr/decr
    apply_and_check(1'b0, 1'b1, 1'b1, 1'b1, 4'd8, 2'd3, 2'd3, 1'b1);

    // Hold
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b0, 4'd0, 2'd0, 2'd0, 1'b1);

    // Directed tests
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd1, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd3, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd1, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd3, 1'b1);

    // Both valid => net effect
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd3, 2'd1, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd1, 2'd3, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd2, 2'd2, 1'b1);

    // Wrap checks
    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd9, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd3, 2'd0, 1'b1); // 9->1

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd1, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd3, 1'b1); // 1->9

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd10, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd1, 2'd0, 1'b1); // 10->0

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd0, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd1, 1'b1); // 0->10

    // Sweep many cases
    for (initv = 0; initv <= 10; initv = initv + 1) begin
      apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, initv[3:0], 2'd0, 2'd0, 1'b1);

      for (a = 0; a <= 3; a = a + 1) begin
        apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, a[1:0], 2'd0, 1'b1);
        apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, a[1:0], 1'b1);

        for (b = 0; b <= 3; b = b + 1) begin
          apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, a[1:0], b[1:0], 1'b1);
        end
      end
    end

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
