
module tb;

  reg [49:0] in;
  reg [2:0] shift;
  reg [4:0] fill;
  wire [49:0] out;
  wire out_valid;

  integer errors;
  integer sh;
  integer sym;
  reg [49:0] expected_out;
  reg expected_valid;
  reg [4:0] in_syms [0:9];
  reg [4:0] expected_sym;

  shift_right dut (
    .out_valid(out_valid),
    .in(in),
    .shift(shift),
    .fill(fill),
    .out(out)
  );

  task load_symbols;
    begin
      in_syms[0] = in[4:0];
      in_syms[1] = in[9:5];
      in_syms[2] = in[14:10];
      in_syms[3] = in[19:15];
      in_syms[4] = in[24:20];
      in_syms[5] = in[29:25];
      in_syms[6] = in[34:30];
      in_syms[7] = in[39:35];
      in_syms[8] = in[44:40];
      in_syms[9] = in[49:45];
    end
  endtask

  task compute_expected;
    begin
      load_symbols();
      expected_out = 50'd0;

      for (sym = 0; sym < 10; sym = sym + 1) begin
        if ((sym + shift) < 10)
          expected_sym = in_syms[sym + shift];
        else
          expected_sym = fill;

        expected_out[sym*5 +: 5] = expected_sym;
      end

      expected_valid = (shift <= 3'd4);
    end
  endtask

  task apply_and_check;
    input [49:0] t_in;
    input [2:0] t_shift;
    input [4:0] t_fill;
    begin
      in = t_in;
      shift = t_shift;
      fill = t_fill;
      #1;

      compute_expected();

      if (out_valid !== expected_valid) begin
        $display("FAIL out_valid mismatch: shift=%0d expected=%0d got=%0d",
                 shift, expected_valid, out_valid);
        errors = errors + 1;
      end

      if (expected_valid && (out !== expected_out)) begin
        $display("FAIL out mismatch: shift=%0d expected=%h got=%h",
                 shift, expected_out, out);
        errors = errors + 1;
      end
    end
  endtask

  initial begin
    errors = 0;

    in = {
      5'd10, 5'd9, 5'd8, 5'd7, 5'd6,
      5'd5, 5'd4, 5'd3, 5'd2, 5'd1
    };
    fill = 5'd31;

    apply_and_check(in, 3'd0, fill);
    apply_and_check(in, 3'd1, fill);
    apply_and_check(in, 3'd2, fill);
    apply_and_check(in, 3'd3, fill);
    apply_and_check(in, 3'd4, fill);

    apply_and_check(in, 3'd5, fill);
    apply_and_check(in, 3'd6, fill);
    apply_and_check(in, 3'd7, fill);

    in = {
      5'h1F, 5'h1E, 5'h1D, 5'h1C, 5'h1B,
      5'h1A, 5'h19, 5'h18, 5'h17, 5'h16
    };
    fill = 5'h0A;
    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

    in = {
      5'd0, 5'd1, 5'd2, 5'd3, 5'd4,
      5'd5, 5'd6, 5'd7, 5'd8, 5'd9
    };
    fill = 5'd0;
    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

    if (errors == 0) begin
      $display("TESTS PASSED");
    end else begin
      $display("TEST FAILED WITH %0d ERRORS", errors);
    end

    $finish;
  end

endmodule
