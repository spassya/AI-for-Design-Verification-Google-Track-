
module tb;

  reg [9:0] bin;
  wire [9:0] gray;

  integer errors;
  integer i;
  reg [9:0] expected;

  enc_bin2gray dut (
    .bin(bin),
    .gray(gray)
  );

  task apply_and_check;
    input [9:0] t_bin;
    begin
      bin = t_bin;
      #1;

      expected = bin ^ (bin >> 1);

      if (gray !== expected) begin
        $display("FAIL bin=%b expected_gray=%b got_gray=%b",
                 bin, expected, gray);
        errors = errors + 1;
      end
    end
  endtask

  initial begin
    errors = 0;

    apply_and_check(10'b0000000000);
    apply_and_check(10'b0000000001);
    apply_and_check(10'b0000000010);
    apply_and_check(10'b0000000011);
    apply_and_check(10'b0000000100);
    apply_and_check(10'b0000000111);
    apply_and_check(10'b0000001000);
    apply_and_check(10'b0000011111);
    apply_and_check(10'b0000100000);
    apply_and_check(10'b0010101010);
    apply_and_check(10'b0101010101);
    apply_and_check(10'b0111111111);
    apply_and_check(10'b1000000000);
    apply_and_check(10'b1111111111);

    for (i = 0; i < 1024; i = i + 1)
      apply_and_check(i[9:0]);

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
