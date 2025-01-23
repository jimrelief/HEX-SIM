//`include "./pe.v"

module systolic_array
#(
    parameter ROWS = 32,
    parameter COLS = 32,
    parameter WORD_SIZE = 16

) (
    clk,
    rst_n,
    //control sign
    prefill,
    os_en,
   

    //data bus
    //result_bus_o,//use for os mode

    left_in_bus,
    top_in_bus,
    bottom_out_bus,
    right_out_bus
);

input clk;
input rst_n;

input [ROWS * WORD_SIZE - 1: 0] left_in_bus;
input [COLS * WORD_SIZE - 1: 0] top_in_bus;
output [COLS * WORD_SIZE - 1: 0] bottom_out_bus;
output [ROWS * WORD_SIZE - 1: 0] right_out_bus;

input prefill;
input os_en;

wire [COLS * ROWS * WORD_SIZE - 1: 0] hor_interconnect;//cols 个 rows* word大小的竖线
wire [ROWS * COLS * WORD_SIZE - 1: 0] ver_interconnect;//rows 个 cols* word 大小的横线
wire [ROWS * COLS * WORD_SIZE - 1: 0] result_bus;

genvar r, c;

generate
for (r = 0; r < ROWS; r = r + 1)
begin
    assign right_out_bus[(r+1) * WORD_SIZE - 1 -: WORD_SIZE] = hor_interconnect[COLS * (r + 1) * WORD_SIZE - 1 -: WORD_SIZE];//最后一行竖线 
end 

for (c  = 0; c < COLS; c = c + 1)
begin
    assign bottom_out_bus[(c+1) * WORD_SIZE - 1 -: WORD_SIZE] = ver_interconnect[ROWS * (c + 1) * WORD_SIZE - 1 -: WORD_SIZE];//最后一行横线
end

for(r = 0; r < ROWS; r = r+1)
begin
    for(c = 0; c < COLS; c = c+1)
    begin

        localparam VERTICAL_SIGNAL_OFFSET = (c * ROWS + (r+1)) * WORD_SIZE;
        localparam HORIZONTAL_SIGNAL_OFFSET = (r * COLS + (c+1)) * WORD_SIZE;
        localparam RESULT_PEER_OFFSET = (c * ROWS + (r+1)) * WORD_SIZE;

        if ((r == 0) && (c==0))
        begin

            pe #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_top_left(
                .clk(clk),
                .rst_n(rst_n),

                .prefill(prefill),
                .os_en(os_en),
                .result(result_bus[RESULT_PEER_OFFSET -1 -:WORD_SIZE]),

                .left_in(left_in_bus[(r+1) * WORD_SIZE -1 -: WORD_SIZE]),
                .top_in(top_in_bus[(c+1) * WORD_SIZE - 1 -: WORD_SIZE]),
                .right_out(hor_interconnect[HORIZONTAL_SIGNAL_OFFSET - 1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
        else if (c==0)
        begin

            localparam TOP_PEER_OFFSET = (c * ROWS + r) * WORD_SIZE;

            pe #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_left_col(
                .clk(clk),
                .rst_n(rst_n),

                .prefill(prefill),
                .os_en(os_en),
                .result(result_bus[RESULT_PEER_OFFSET -1 -:WORD_SIZE]),

                .left_in(left_in_bus[(r+1) * WORD_SIZE -1 -: WORD_SIZE]),
                .top_in(ver_interconnect[TOP_PEER_OFFSET -1 -: WORD_SIZE]),
                .right_out(hor_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
        else if (r==0)
        begin

            localparam LEFT_PEER_OFFSET = (r * COLS + c) * WORD_SIZE;

            pe #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_top_row(
                .clk(clk),
                .rst_n(rst_n),

                .prefill(prefill),
                .os_en(os_en),
                .result(result_bus[RESULT_PEER_OFFSET -1 -:WORD_SIZE]),

                .left_in(hor_interconnect[LEFT_PEER_OFFSET - 1 -: WORD_SIZE]),
                .top_in(top_in_bus[(c+1) * WORD_SIZE - 1 -: WORD_SIZE]),
                .right_out(hor_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
        else
        begin

            localparam TOP_PEER_OFFSET =  (c * ROWS + r)  * WORD_SIZE;
            localparam LEFT_PEER_OFFSET = (r * COLS + c) * WORD_SIZE;
            
            pe #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_rest(
                .clk(clk),
                .rst_n(rst_n),

                .prefill(prefill),
                .os_en(os_en),
                .result(result_bus[RESULT_PEER_OFFSET -1 -:WORD_SIZE]),

                .left_in(hor_interconnect[LEFT_PEER_OFFSET - 1 -: WORD_SIZE]),
                .top_in(ver_interconnect[TOP_PEER_OFFSET -1 -: WORD_SIZE]),
                .right_out(hor_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
    end
end
endgenerate

endmodule
