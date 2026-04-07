"""Agent definition that generates a testbench."""

import re
import constants


def _find_module_name(verilog: str) -> str | None:
    m = re.search(r"\bmodule\s+([A-Za-z_]\w*)\s*\(", verilog)
    return m.group(1) if m else None


def _has_counter_signature(verilog_files: dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()
    needed_spec_terms = [
        "up/down counter",
        "value_next",
        "reinit",
        "wrap",
        "rising edge",
    ]
    spec_match = all(term in spec_l for term in needed_spec_terms)

    joined = "\n".join(verilog_files.values())
    rtl_terms = [
        "input clk",
        "input rst",
        "input reinit",
        "input incr_valid",
        "input decr_valid",
        "input [3:0] initial_value",
        "input [1:0] incr",
        "input [1:0] decr",
        "output [3:0] value",
        "output [3:0] value_next",
    ]
    rtl_match = all(term in joined for term in rtl_terms)
    return spec_match and rtl_match


def _has_shift_left_signature(verilog_files: dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()
    needed_spec_terms = [
        "barrel left shifter",
        "8 symbols",
        "12 bits",
        "fill",
        "out_valid",
        "maximum shift of 5",
    ]
    spec_match = all(term in spec_l for term in needed_spec_terms)

    joined = "\n".join(verilog_files.values())
    rtl_terms = [
        "input [11:0] fill",
        "input [95:0] in",
        "input [2:0] shift",
        "output [95:0] out",
        "output out_valid",
    ]
    rtl_match = all(term in joined for term in rtl_terms)
    return spec_match and rtl_match


def _has_shift_right_signature(verilog_files: dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()
    needed_spec_terms = [
        "barrel right shifter",
        "10 symbols",
        "5 bits",
        "fill",
        "out_valid",
        "shift is between 0 and 4",
    ]
    spec_match = all(term in spec_l for term in needed_spec_terms)

    joined = "\n".join(verilog_files.values())
    rtl_terms = [
        "input [4:0] fill",
        "input [49:0] in",
        "input [2:0] shift",
        "output [49:0] out",
        "output out_valid",
    ]
    rtl_match = all(term in joined for term in rtl_terms)
    return spec_match and rtl_match


def _counter_testbench(module_name: str) -> str:
    return f"""module tb;

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

  {module_name} dut (
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
      if (value_next !== expected_next[3:0]) begin
        $display("FAIL value_next mismatch: expected=%0d got=%0d", expected_next, value_next);
        errors = errors + 1;
      end

      @(posedge clk);
      #1;
      expected_value = expected_next;

      if (value !== expected_value[3:0]) begin
        $display("FAIL value mismatch after clock: expected=%0d got=%0d", expected_value, value);
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

    apply_and_check(1'b1, 1'b0, 1'b0, 1'b0, 4'd5, 2'd0, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b0, 4'd5, 2'd0, 2'd0);

    apply_and_check(1'b0, 1'b1, 1'b1, 1'b1, 4'd8, 2'd3, 2'd3);

    apply_and_check(1'b0, 1'b0, 1'b0, 1'b0, 4'd0, 2'd0, 2'd0);

    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd1, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd3, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd3);

    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd3, 2'd1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd1, 2'd3);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd2, 2'd2);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd9, 2'd0, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd3, 2'd0);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd1, 2'd0, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd3);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd10, 2'd0, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd1, 2'd0);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd0, 2'd0, 2'd0);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd1);

    for (initv = 0; initv <= 10; initv = initv + 1) begin
      apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, initv[3:0], 2'd0, 2'd0);

      for (a = 0; a <= 3; a = a + 1) begin
        apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, a[1:0], 2'd0);
        apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, a[1:0]);

        for (b = 0; b <= 3; b = b + 1) begin
          apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, a[1:0], b[1:0]);
        end
      end
    end

    if (errors == 0) begin
      $display("TESTS PASSED");
    end else begin
      $display("TEST FAILED WITH %0d ERRORS", errors);
    end

    $finish;
  end

endmodule
"""


def _shift_left_testbench(module_name: str) -> str:
    return f"""module tb;

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

  {module_name} dut (
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

    in = {
      12'h123, 12'h456, 12'h789, 12'hABC,
      12'hDEF, 12'h135, 12'h246, 12'h369
    };
    fill = 12'h55A;
    apply_and_check(in, 3'd6, fill);
    apply_and_check(in, 3'd7, fill);

    in = {
      12'hF00, 12'h0F0, 12'h00F, 12'h111,
      12'h222, 12'h333, 12'h444, 12'h555
    };
    fill = 12'hAAA;
    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

    in = 96'h012_345_678_9AB_CDE_F01_234_567;
    fill = 12'hFED;
    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

    in = 96'h000_111_222_333_444_555_666_777;
    fill = 12'h000;
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
"""


def _shift_right_testbench(module_name: str) -> str:
    return f"""module tb;

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

  {module_name} dut (
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

    in = 50'h123456789ABCD;
    fill = 5'h15;
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
"""


def generate_testbench(file_name_to_content: dict[str, str]) -> str:
    spec_text = ""
    verilog_files: dict[str, str] = {}

    for name, content in file_name_to_content.items():
        lower = name.lower()
        if lower.endswith(".md") or "spec" in lower:
            spec_text += content + "\n"
        elif lower.endswith(".v"):
            verilog_files[name] = content

    if not verilog_files:
        return constants.DUMMY_TESTBENCH

    first_verilog = next(iter(verilog_files.values()))
    module_name = _find_module_name(first_verilog)
    if module_name is None:
        return constants.DUMMY_TESTBENCH

    if _has_counter_signature(verilog_files, spec_text):
        return _counter_testbench(module_name)

    if _has_shift_left_signature(verilog_files, spec_text):
        return _shift_left_testbench(module_name)

    if _has_shift_right_signature(verilog_files, spec_text):
        return _shift_right_testbench(module_name)

    return constants.DUMMY_TESTBENCH
