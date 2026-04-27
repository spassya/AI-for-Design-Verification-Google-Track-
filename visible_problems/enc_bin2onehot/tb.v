
module tb;

  reg clk;
  reg rst;
  reg [3:0] in;
  reg in_valid;
  wire [14:0] out;

  integer errors;
  integer i;
  reg [14:0] expected;

  enc_bin2onehot dut (
    .clk(clk),
    .rst(rst),
    .in(in),
    .in_valid(in_valid),
    .out(out)
  );

  always #5 clk = ~clk;

  task apply_and_check;
    input [3:0] t_in;
    input t_valid;
    begin
      in = t_in;
      in_valid = t_valid;
      #1;

      if (t_valid && t_in <= 4'd14)
        expected = (15'b1 << t_in);
      else
        expected = 15'b0;

      if (out !== expected) begin
        $display("FAIL in=%0d valid=%0d expected=%b got=%b",
                 in, in_valid, expected, out);
        errors = errors + 1;
      end
    end
  endtask

  initial begin
    clk = 0;
    rst = 0;
    errors = 0;

    apply_and_check(4'd0, 1'b0);
    apply_and_check(4'd5, 1'b0);
    apply_and_check(4'd14, 1'b0);

    for (i = 0; i <= 14; i = i + 1)
      apply_and_check(i[3:0], 1'b1);

    apply_and_check(4'd0, 1'b1);
    apply_and_check(4'd1, 1'b1);
    apply_and_check(4'd2, 1'b1);
    apply_and_check(4'd7, 1'b1);
    apply_and_check(4'd14, 1'b1);

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
