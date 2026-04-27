
module tb;

  reg clk;
  reg rst;
  reg data_valid;
  reg [11:0] data;
  wire enc_valid;
  wire [12:0] enc_codeword;

  integer errors;
  integer i;
  reg [12:0] expected_codeword;
  reg expected_valid;

  ecc_sed_encoder dut (
    .clk(clk),
    .rst(rst),
    .data_valid(data_valid),
    .data(data),
    .enc_valid(enc_valid),
    .enc_codeword(enc_codeword)
  );

  always #5 clk = ~clk;

  task apply_and_check;
    input [11:0] t_data;
    input t_valid;
    begin
      data = t_data;
      data_valid = t_valid;
      #1;

      expected_valid = t_valid;
      expected_codeword = {^t_data, t_data};

      if (enc_valid !== expected_valid) begin
        $display("FAIL enc_valid data=%h valid=%0d expected=%0d got=%0d",
                 data, data_valid, expected_valid, enc_valid);
        errors = errors + 1;
      end

      if (t_valid && enc_codeword !== expected_codeword) begin
        $display("FAIL enc_codeword data=%h expected=%b got=%b",
                 data, expected_codeword, enc_codeword);
        errors = errors + 1;
      end

      if (t_valid && (^enc_codeword !== 1'b0)) begin
        $display("FAIL codeword parity not even: data=%h codeword=%b",
                 data, enc_codeword);
        errors = errors + 1;
      end
    end
  endtask

  initial begin
    clk = 0;
    rst = 0;
    errors = 0;
    data = 0;
    data_valid = 0;

    // Invalid input: only enc_valid is checked
    apply_and_check(12'h000, 1'b0);
    apply_and_check(12'hFFF, 1'b0);
    apply_and_check(12'hA5A, 1'b0);

    // Directed valid cases
    apply_and_check(12'h000, 1'b1);
    apply_and_check(12'h001, 1'b1);
    apply_and_check(12'h002, 1'b1);
    apply_and_check(12'h003, 1'b1);
    apply_and_check(12'h555, 1'b1);
    apply_and_check(12'hAAA, 1'b1);
    apply_and_check(12'hFFF, 1'b1);
    apply_and_check(12'h800, 1'b1);
    apply_and_check(12'h7FF, 1'b1);

    // Sweep all one-hot data bits
    for (i = 0; i < 12; i = i + 1)
      apply_and_check(12'b1 << i, 1'b1);

    // More pattern coverage
    for (i = 0; i < 64; i = i + 1)
      apply_and_check((i * 12'h25) & 12'hFFF, 1'b1);

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
