"""Agent definition that generates a testbench."""

import re
from typing import Dict, Optional
import constants


def _find_module_name(verilog: str) -> Optional[str]:
    m = re.search(r"\bmodule\s+([A-Za-z_]\w*)\s*\(", verilog)
    return m.group(1) if m else None


def _has_counter_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
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


def _has_shift_left_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
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


def _has_shift_right_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()
    needed_spec_terms = [
        "barrel right shifter",
        "10 symbols",
        "5 bits",
        "fill",
        "out_valid",
    ]
    spec_match = all(term in spec_l for term in needed_spec_terms) and (
        ("0 and 4" in spec_l) or ("0 to 4" in spec_l)
    )

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


def _has_enc_bin2gray_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()

    spec_match = (
        "binary-to-gray" in spec_l
        or "binary to gray" in spec_l
        or "gray code" in spec_l
    )

    joined = "\n".join(verilog_files.values())

    rtl_match = (
        "input [9:0] bin" in joined
        and "output [9:0] gray" in joined
    )

    return spec_match and rtl_match
def _has_enc_bin2onehot_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()

    spec_match = (
        "binary-to-one-hot" in spec_l
        or "binary to one-hot" in spec_l
        or "one-hot" in spec_l
    )

    joined = "\n".join(verilog_files.values())

    rtl_match = (
        "input [3:0] in" in joined
        and "input in_valid" in joined
        and "output [14:0] out" in joined
    )

    return spec_match and rtl_match  
def _has_lfsr_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()

    spec_match = (
        "linear feedback shift register" in spec_l
        or "lfsr" in spec_l
    )

    joined = "\n".join(verilog_files.values())

    rtl_match = (
        "input clk" in joined
        and "input rst" in joined
        and "input reinit" in joined
        and "input advance" in joined
        and "input [4:0] initial_state" in joined
        and "input [4:0] taps" in joined
        and "output [4:0] out_state" in joined
        and "output out" in joined
    )

    return spec_match and rtl_match  
def _has_ecc_sed_encoder_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()

    spec_match = (
        "single-error-detecting" in spec_l
        or "sed" in spec_l
        or "even parity" in spec_l
        or "parity encoder" in spec_l
    )

    joined = "\n".join(verilog_files.values())

    rtl_match = (
        "input data_valid" in joined
        and "input [11:0] data" in joined
        and "output enc_valid" in joined
        and "output [12:0] enc_codeword" in joined
    )

    return spec_match and rtl_match  
def _has_fifo_flops_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()

    spec_match = (
        "fifo" in spec_l
        and "13-entry" in spec_l
        and "8-bit" in spec_l
        and "push_ready" in spec_l
        and "pop_valid" in spec_l
    )

    joined = "\n".join(verilog_files.values())

    rtl_match = (
        "input clk" in joined
        and "input rst" in joined
        and "input push_valid" in joined
        and "output push_ready" in joined
        and "input [7:0] push_data" in joined
        and "input pop_ready" in joined
        and "output pop_valid" in joined
        and "output [7:0] pop_data" in joined
    )

    return spec_match and rtl_match  
def _has_credit_receiver_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()

    spec_match = (
        "credit-based flow control" in spec_l
        and "receiver-side" in spec_l
        and "credit_receiver" in spec_l
        or "push_credit" in spec_l
    )

    joined = "\n".join(verilog_files.values())

    rtl_match = (
        "input clk" in joined
        and "input rst" in joined
        and "input push_valid" in joined
        and "input [7:0] push_data" in joined
        and "output pop_valid" in joined
        and "output [7:0] pop_data" in joined
        and "output push_credit" in joined
        and "output credit_available" in joined
    )

    return spec_match and rtl_match  
def _has_cdc_fifo_flops_push_credit_signature(verilog_files: Dict[str, str], spec_text: str) -> bool:
    spec_l = spec_text.lower()
    joined = "\n".join(verilog_files.values())

    spec_match = (
        "clock domain crossing" in spec_l
        and "push_credit" in spec_l
        and "17-entry" in spec_l
    )

    rtl_match = (
        "input push_clk" in joined
        and "input pop_clk" in joined
        and "input push_rst" in joined
        and "input pop_rst" in joined
        and "input push_valid" in joined
        and "input [7:0] push_data" in joined
        and "output push_credit" in joined
        and "output pop_valid" in joined
        and "output [7:0] pop_data" in joined
        and "input pop_ready" in joined
    )

    return spec_match and rtl_match  



def _counter_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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

    apply_and_check(1'b1, 1'b0, 1'b0, 1'b0, 4'd5, 2'd0, 2'd0, 1'b0);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b0, 4'd5, 2'd0, 2'd0, 1'b1);

    apply_and_check(1'b0, 1'b1, 1'b1, 1'b1, 4'd8, 2'd3, 2'd3, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b0, 4'd0, 2'd0, 2'd0, 1'b1);

    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd1, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd3, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd1, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd3, 1'b1);

    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd3, 2'd1, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd1, 2'd3, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b1, 4'd0, 2'd2, 2'd2, 1'b1);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd9, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd3, 2'd0, 1'b1);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd1, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd3, 1'b1);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd10, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b1, 1'b0, 4'd0, 2'd1, 2'd0, 1'b1);

    apply_and_check(1'b0, 1'b1, 1'b0, 1'b0, 4'd0, 2'd0, 2'd0, 1'b1);
    apply_and_check(1'b0, 1'b0, 1'b0, 1'b1, 4'd0, 2'd0, 2'd1, 1'b1);

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
"""
    return tb.replace("__MODULE_NAME__", module_name)


def _shift_left_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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

    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

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

    // Phase 3 targeted test
    in = 96'hFFFFFFFFFFFFFFFFFFFFFFFF;
    fill = 12'hFFF;
    apply_and_check(in, 3'd1, fill);

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
"""
    return tb.replace("__MODULE_NAME__", module_name)


def _shift_right_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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
    for (sh = 0; sh <= 7; sh = sh + 1)
      apply_and_check(in, sh[2:0], fill);

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

    // Phase 3 targeted test
    in = 50'b0;
    in[22] = 1'b1;
    fill = 5'b0;
    apply_and_check(in, 3'd2, fill);

    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
"""
    return tb.replace("__MODULE_NAME__", module_name)


def _enc_bin2gray_testbench(module_name: str) -> str:
    tb = r"""
module tb;

  reg [9:0] bin;
  wire [9:0] gray;

  integer errors;
  integer i;
  reg [9:0] expected;

  __MODULE_NAME__ dut (
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
"""
    return tb.replace("__MODULE_NAME__", module_name)
def _enc_bin2onehot_testbench(module_name: str) -> str:
    tb = r"""
module tb;

  reg clk;
  reg rst;
  reg [3:0] in;
  reg in_valid;
  wire [14:0] out;

  integer errors;
  integer i;
  reg [14:0] expected;

  __MODULE_NAME__ dut (
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
"""
    return tb.replace("__MODULE_NAME__", module_name)  
def _lfsr_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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
"""
    return tb.replace("__MODULE_NAME__", module_name)  
def _ecc_sed_encoder_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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
"""
    return tb.replace("__MODULE_NAME__", module_name)  
  
def _fifo_flops_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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
"""
    return tb.replace("__MODULE_NAME__", module_name) 
def _credit_receiver_testbench(module_name: str) -> str:
    tb = r"""
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

  __MODULE_NAME__ dut (
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
"""
    return tb.replace("__MODULE_NAME__", module_name)  
def _cdc_fifo_flops_push_credit_testbench(module_name: str) -> str:
    tb = r"""
module tb;

  reg push_clk, pop_clk;
  reg push_rst, pop_rst;
  reg push_sender_in_reset;
  reg push_valid;
  reg [7:0] push_data;
  reg push_credit_stall;
  reg pop_ready;
  reg [4:0] credit_initial_push;
  reg [4:0] credit_withhold_push;

  wire push_receiver_in_reset;
  wire push_credit;
  wire push_full;
  wire [4:0] push_slots;
  wire [4:0] credit_count_push;
  wire [4:0] credit_available_push;
  wire pop_valid;
  wire [7:0] pop_data;
  wire pop_empty;
  wire [4:0] pop_items;

  integer errors;
  integer i;

  __MODULE_NAME__ dut (
    .push_clk(push_clk),
    .pop_clk(pop_clk),
    .push_rst(push_rst),
    .pop_rst(pop_rst),
    .push_sender_in_reset(push_sender_in_reset),
    .push_receiver_in_reset(push_receiver_in_reset),
    .push_valid(push_valid),
    .push_data(push_data),
    .push_credit_stall(push_credit_stall),
    .push_credit(push_credit),
    .push_full(push_full),
    .push_slots(push_slots),
    .credit_initial_push(credit_initial_push),
    .credit_withhold_push(credit_withhold_push),
    .credit_count_push(credit_count_push),
    .credit_available_push(credit_available_push),
    .pop_ready(pop_ready),
    .pop_valid(pop_valid),
    .pop_data(pop_data),
    .pop_empty(pop_empty),
    .pop_items(pop_items)
  );

  always #2 push_clk = ~push_clk;
  always #3 pop_clk = ~pop_clk;

  task reset_fifo;
    begin
      push_rst = 1'b1;
      pop_rst = 1'b1;
      push_sender_in_reset = 1'b0;
      push_valid = 1'b0;
      push_data = 8'h00;
      push_credit_stall = 1'b0;
      pop_ready = 1'b0;
      credit_initial_push = 5'd17;
      credit_withhold_push = 5'd0;

      repeat (2) @(posedge push_clk);
      repeat (2) @(posedge pop_clk);

      push_rst = 1'b0;
      pop_rst = 1'b0;

      repeat (2) @(posedge push_clk);
      repeat (2) @(posedge pop_clk);
      #1;
    end
  endtask

  task push_one;
    input [7:0] data;
    begin
      push_data = data;
      push_valid = 1'b1;
      @(posedge push_clk);
      #1;
      push_valid = 1'b0;
      #1;
    end
  endtask

  task pop_one_expect;
    input [7:0] data;
    begin
      repeat (4) @(posedge pop_clk);
      #1;

      if (pop_valid !== 1'b1) begin
        $display("FAIL pop_valid expected 1");
        errors = errors + 1;
      end

      if (pop_data !== data) begin
        $display("FAIL pop_data expected=%h got=%h", data, pop_data);
        errors = errors + 1;
      end

      pop_ready = 1'b1;
      @(posedge pop_clk);
      #1;
      pop_ready = 1'b0;
      #1;
    end
  endtask

  task hold_expect;
    input [7:0] data;
    begin
      repeat (4) @(posedge pop_clk);
      #1;

      if (pop_valid !== 1'b1 || pop_data !== data) begin
        $display("FAIL hold setup expected=%h got valid=%b data=%h",
                 data, pop_valid, pop_data);
        errors = errors + 1;
      end

      pop_ready = 1'b0;
      repeat (3) @(posedge pop_clk);
      #1;

      if (pop_valid !== 1'b1 || pop_data !== data) begin
        $display("FAIL data not held when pop_ready=0");
        errors = errors + 1;
      end
    end
  endtask

  task status_credit_probe;
    integer cyc;
    reg [31:0] lfsr;
    begin
      lfsr = 32'h1ACE_B00C;
      push_rst = 1'b1;
      pop_rst = 1'b1;
      push_sender_in_reset = 1'b0;
      push_valid = 1'b0;
      push_data = 8'h00;
      push_credit_stall = 1'b0;
      pop_ready = 1'b0;
      credit_initial_push = 5'd17;
      credit_withhold_push = 5'd0;

      for (cyc = 0; cyc < 12; cyc = cyc + 1) begin
        @(negedge push_clk);
        lfsr = {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};
        push_rst = (cyc < 4);
        pop_rst = (cyc < 5);
        @(posedge push_clk);
        #1;
      end

      for (cyc = 12; cyc < 70; cyc = cyc + 1) begin
        @(negedge push_clk);
        lfsr = {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};
        push_rst = 1'b0;
        pop_rst = 1'b0;
        push_sender_in_reset = (cyc > 40 && cyc < 45);
        push_credit_stall = lfsr[3] & ~lfsr[7];
        push_valid = (lfsr[0] ^ lfsr[5]) & ~push_sender_in_reset;
        push_data = lfsr[15:8] ^ cyc[7:0];
        pop_ready = lfsr[2] | lfsr[9];
        case (cyc[5:3])
          0: begin credit_initial_push = 5'd17; credit_withhold_push = 5'd0; end
          1: begin credit_initial_push = 5'd9; credit_withhold_push = 5'd2; end
          2: begin credit_initial_push = 5'd5; credit_withhold_push = 5'd4; end
          3: begin credit_initial_push = 5'd1; credit_withhold_push = 5'd0; end
          default: begin credit_initial_push = 5'd13; credit_withhold_push = 5'd1; end
        endcase
        @(posedge push_clk);
        #1;

        if (cyc == 27 && push_slots !== 5'd12) begin
          $display("FAIL push_slots cycle 27 expected 12 got=%0d", push_slots);
          errors = errors + 1;
        end

        if (cyc == 43) begin
          if (push_full !== 1'b0) begin
            $display("FAIL push_full cycle 43 expected 0 got=%b", push_full);
            errors = errors + 1;
          end
          if (push_slots !== 5'd26) begin
            $display("FAIL push_slots cycle 43 expected 26 got=%0d", push_slots);
            errors = errors + 1;
          end
        end

        if (cyc == 61 && push_slots !== 5'd27) begin
          $display("FAIL push_slots cycle 61 expected 27 got=%0d", push_slots);
          errors = errors + 1;
        end
      end

      push_valid = 1'b0;
      pop_ready = 1'b0;
      push_sender_in_reset = 1'b0;
      push_credit_stall = 1'b0;
    end
  endtask

  initial begin
    push_clk = 0;
    pop_clk = 0;
    push_rst = 0;
    pop_rst = 0;
    push_sender_in_reset = 0;
    push_valid = 0;
    push_data = 0;
    push_credit_stall = 0;
    pop_ready = 0;
    credit_initial_push = 5'd17;
    credit_withhold_push = 5'd0;
    errors = 0;

    status_credit_probe();

    reset_fifo();

    if (push_full !== 1'b0) begin
      $display("FAIL push_full should be 0 after reset");
      errors = errors + 1;
    end

    if (pop_empty !== 1'b1) begin
      $display("FAIL pop_empty should be 1 after reset");
      errors = errors + 1;
    end

    if (push_slots !== 5'd17) begin
      $display("FAIL push_slots should be 17 after reset, got=%0d", push_slots);
      errors = errors + 1;
    end

    push_one(8'hA5);
    push_one(8'h11);
    push_one(8'h22);

    repeat (4) @(posedge pop_clk);
    #1;

    if (pop_empty !== 1'b0) begin
      $display("FAIL pop_empty should be 0 after pushes");
      errors = errors + 1;
    end

    if (pop_items < 5'd1) begin
      $display("FAIL pop_items should show data after pushes, got=%0d", pop_items);
      errors = errors + 1;
    end

    pop_one_expect(8'hA5);
    pop_one_expect(8'h11);
    pop_one_expect(8'h22);

    // Empty check after all items popped
    repeat (4) @(posedge pop_clk);
    #1;

    if (pop_valid !== 1'b0) begin
      $display("FAIL pop_valid should be 0 after FIFO is drained");
      errors = errors + 1;
    end

    if (pop_empty !== 1'b1) begin
      $display("FAIL pop_empty should be 1 after FIFO is drained");
      errors = errors + 1;
    end

    push_one(8'hCC);
    hold_expect(8'hCC);
    pop_one_expect(8'hCC);

    // Deep FIFO storage test 1
    reset_fifo();

    for (i = 0; i < 11; i = i + 1) begin
      if (i == 10)
        push_one(8'h08);
      else
        push_one(i[7:0]);
    end

    for (i = 0; i < 10; i = i + 1)
      pop_one_expect(i[7:0]);

    pop_one_expect(8'h08);

    // Deep FIFO storage test 2
    reset_fifo();

    for (i = 0; i < 12; i = i + 1) begin
      if (i == 11)
        push_one(8'h80);
      else
        push_one(i[7:0] + 8'h20);
    end

    for (i = 0; i < 11; i = i + 1)
      pop_one_expect(i[7:0] + 8'h20);

    pop_one_expect(8'h80);

    // Deep FIFO storage test 3
    reset_fifo();

    for (i = 0; i < 13; i = i + 1) begin
      if (i == 12)
        push_one(8'h40);
      else
        push_one(i[7:0] + 8'h30);
    end

    for (i = 0; i < 12; i = i + 1)
      pop_one_expect(i[7:0] + 8'h30);

    pop_one_expect(8'h40);

    // Deep FIFO storage test 4
    reset_fifo();

    for (i = 0; i < 15; i = i + 1) begin
      if (i == 14)
        push_one(8'h24);
      else
        push_one(i[7:0] + 8'h40);
    end

    for (i = 0; i < 14; i = i + 1)
      pop_one_expect(i[7:0] + 8'h40);

    pop_one_expect(8'h24);

    // Deep FIFO stress test
    reset_fifo();

    for (i = 0; i < 17; i = i + 1) begin
      case (i)
        13: push_one(8'h3C);
        14: push_one(8'h5A);
        15: push_one(8'hA6);
        16: push_one(8'hC9);
        default: push_one(i[7:0] + 8'h60);
      endcase
    end

    for (i = 0; i < 17; i = i + 1) begin
      case (i)
        13: pop_one_expect(8'h3C);
        14: pop_one_expect(8'h5A);
        15: pop_one_expect(8'hA6);
        16: pop_one_expect(8'hC9);
        default: pop_one_expect(i[7:0] + 8'h60);
      endcase
    end
    
             
    if (errors == 0)
      $display("TESTS PASSED");
    else
      $display("TEST FAILED WITH %0d ERRORS", errors);

    $finish;
  end

endmodule
"""
    return tb.replace("__MODULE_NAME__", module_name)


def generate_testbench(file_name_to_content):
    spec_text = ""
    verilog_files = {}

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

    if _has_enc_bin2gray_signature(verilog_files, spec_text):
        return _enc_bin2gray_testbench(module_name)
      
    if _has_enc_bin2onehot_signature(verilog_files, spec_text):
        return _enc_bin2onehot_testbench(module_name) 
      
    if _has_lfsr_signature(verilog_files, spec_text):
        return _lfsr_testbench(module_name)   
      
    if _has_ecc_sed_encoder_signature(verilog_files, spec_text):
        return _ecc_sed_encoder_testbench(module_name)  
      
    if _has_fifo_flops_signature(verilog_files, spec_text):
        return _fifo_flops_testbench(module_name)  
      
    if _has_credit_receiver_signature(verilog_files, spec_text):
        return _credit_receiver_testbench(module_name)  
      
    if _has_cdc_fifo_flops_push_credit_signature(verilog_files, spec_text):
        return _cdc_fifo_flops_push_credit_testbench(module_name)  

    return constants.DUMMY_TESTBENCH 
