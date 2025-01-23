
module pe 
#(
    parameter WORD_SIZE = 16
)(
    clk,
    rst_n,
    
    //Control Signals
    prefill, //is or ws mode prefill data
    os_en, //os mode enable 

    result, // use for os mode

    // Data ports
    left_in,
    top_in, 
    right_out,
    bottom_out
);

/*sign*/
/*=================================================================================================*/
input clk;
input rst_n;

input prefill;
input os_en;
output [WORD_SIZE - 1: 0] result;

input [WORD_SIZE - 1: 0] left_in;
input [WORD_SIZE - 1: 0] top_in;

output [WORD_SIZE - 1: 0] right_out;
output [WORD_SIZE - 1: 0] bottom_out;
/*=================================================================================================*/

reg [WORD_SIZE - 1: 0] top_in_reg;
reg [WORD_SIZE - 1: 0] left_in_reg;
reg [WORD_SIZE - 1: 0] stationary_operand_reg;//os mode reg
reg [WORD_SIZE - 1: 0] accumulator_reg;

wire [WORD_SIZE - 1: 0] multiplier_out;
wire [WORD_SIZE - 1: 0] adder_out; 
wire [WORD_SIZE - 1: 0] mult_op2_mux_out;
wire [WORD_SIZE - 1: 0] add_op2_mux_out;

/*=================================================================================================*/
always @(posedge clk or negedge rst_n) begin
    if(rst_n == 1'b0) begin
        top_in_reg <= 0; 
        left_in_reg <= 0; 
    end else begin 
        left_in_reg <= left_in;
        top_in_reg <= top_in;
    end
end

always @(posedge clk or negedge rst_n ) begin
    if(rst_n == 1'b0) begin
        accumulator_reg <= 0; 
        stationary_operand_reg <= 0; 
    end else begin
        if (prefill == 1'b1) begin
            stationary_operand_reg <= top_in;
        end
        accumulator_reg <= adder_out;
    end
end

/*=================================================================================================*/
assign mult_op2_mux_out = (os_en == 1'b0) ? stationary_operand_reg : top_in_reg;
assign add_op2_mux_out = (os_en == 1'b0) ? top_in_reg : accumulator_reg;

assign multiplier_out = left_in_reg * mult_op2_mux_out;
assign adder_out = multiplier_out + add_op2_mux_out;
/*=================================================================================================*/
assign right_out = left_in_reg;
assign bottom_out = (prefill==1'b1)?  top_in_reg : (os_en ? top_in_reg:adder_out);

assign result = {WORD_SIZE{os_en}} &  adder_out;

endmodule
