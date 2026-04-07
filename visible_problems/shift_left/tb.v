
module tb;

  reg [95:0] in;
  reg [2:0] shift;
  reg [11:0] fill;
  wire [95:0] out;
  wire out_valid;

  integer errors;
  integer sh;
  integer sym;
  reg [95:0] expected_out;
  reg expected_valid;
  reg [11:0] in_syms [0:7];
  reg [11:0] expected_sym;

  shift_left dut (
    .out_valid(out_valid),
    .in(in),
    .shift(shift),
    .fill(fill),
    .out(out)
  );

  task load_symbols;
    begin
      in_syms[0] = in[11:0];
      in_syms[1] = in[23:12];
      in_syms[2] = in[35:24];
      in_syms[3] = in[47:36];
      in_syms[4] = in[59:48];
      in_syms[5] = in[71:60];
      in_syms[6] = in[83:72];
      in_syms[7] = in[95:84];
    end
  endtask

  task compute_expected;
    begin
      load_symbols();
      expected_out = 96'd0;

      for (sym = 0; sym < 8; sym = sym + 1) begin
        if (sym < shift)
          expected_sym = fill;
        else
          expected_sym = in_syms[sym - shift];

        expected_out[sym*12 +: 12] = expected_sym;
      end

      expected_valid = (shift <= 3'd5);
    end
  endtask

  task apply_and_check;
    input [95:0] t_in;
    input [2:0] t_shift;
    input [11:0] t_fill;
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
      12'h008, 12'h007, 12'h006, 12'h005,
      12'h004, 12'h003, 12'h002, 12'h001
    };
    fill = 12'hABC;

    apply_and_check(in, 3'd0, fill);
    apply_and_check(in, 3'd1, fill);
    apply_and_check(in, 3'd2, fill);
    apply_and_check(in, 3'd3, fill);
    apply_and_check(in, 3'd4, fill);
    apply_and_check(in, 3'd5, fill);

    apply_and_check(in, 3'd6, fill);
    apply_and_check(in, 3'd7, fill);

    in = {
      12'h123, 12'h456, 12'h789, 12'hABC,
      12'hDEF, 12'h135, 12'h246, 12'h369
    };
    fill = 12'h55A;
    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

    in = {
      12'hF00, 12'h0F0, 12'h00F, 12'h111,
      12'h222, 12'h333, 12'h444, 12'h555
    };
    fill = 12'hAAA;
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
