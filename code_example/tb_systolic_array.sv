
`timescale 1ns/1ps
//随机化输入矩阵和权重矩阵
class random_dnn;
	logic [16-1:0] input1 = $urandom_range(1,5);
	logic [16-1:0] input2 = $urandom_range(1,5);
	logic [16-1:0] input3 = $urandom_range(1,5);
	logic [16-1:0] input4 = $urandom_range(1,5);
	logic [16-1:0] weight1 = $urandom_range(1,5);
	logic [16-1:0] weight2 = $urandom_range(1,5);
	logic [16-1:0] weight3 = $urandom_range(1,5);
	logic [16-1:0] weight4 = $urandom_range(1,5);

	//1 input error 2 weight error 3 output error
	logic [1:0] error_type = $urandom_range(0,3);

	logic [3:0] error =  $urandom_range(0,20);
endclass

module tb_systolic_array (); /* this is automatically generated */

	// clock
	logic clk;
	initial begin
		clk = 1'b0;
		forever #(0.5) clk = ~clk;
	end

	// asynchronous reset
	logic rst_n;
	initial begin
		rst_n <= 1'b0;
		repeat(1)@(posedge clk);
		rst_n <= 1'b1;
	end

	// (*NOTE*) replace reset, clock, others
	parameter                      ROWS = 2;
	parameter                      COLS = 2;
	parameter                 WORD_SIZE = 16;
	// localparam   VERTICAL_SIGNAL_OFFSET = (c * ROWS + (r+1)) * WORD_SIZE;
	// localparam HORIZONTAL_SIGNAL_OFFSET = (r * COLS + (c+1)) * WORD_SIZE;
	// localparam          TOP_PEER_OFFSET = (c * ROWS + r) * WORD_SIZE;
	// localparam         LEFT_PEER_OFFSET = (r * COLS + c) * WORD_SIZE;
	// localparam          TOP_PEER_OFFSET = (c * ROWS + r) * WORD_SIZE;
	// localparam         LEFT_PEER_OFFSET = (r * COLS + c) * WORD_SIZE;

	logic                           prefill;
	logic                           os_en;
	//logic [COLS * ROWS * WORD_SIZE : 0] result_bus;
	logic [ROWS * WORD_SIZE - 1: 0] left_in_bus;
	logic [COLS * WORD_SIZE - 1: 0] top_in_bus;
	logic [COLS * WORD_SIZE - 1: 0] bottom_out_bus;
	logic [ROWS * WORD_SIZE - 1: 0] right_out_bus;

	logic [16-1:0] actual_input1;
	logic [16-1:0] actual_input2;
	logic [16-1:0] actual_input3;
	logic [16-1:0] actual_input4;

	logic [16-1:0] actual_weight1;
	logic [16-1:0] actual_weight2;
	logic [16-1:0] actual_weight3;
	logic [16-1:0] actual_weight4;

	logic [WORD_SIZE - 1:0] actual_result1,actual_result2,actual_result3,actual_result4;
	logic [WORD_SIZE - 1:0] result1,result2,result3,result4;
	//错误类型
	logic [1:0] error_type;
	//错误标志
	logic [3:0] error_flag;


	systolic_array #(
			.ROWS(ROWS),
			.COLS(COLS),
			.WORD_SIZE(WORD_SIZE)
		) inst_systolic_array (
			.clk            (clk),
			.rst_n         (rst_n),
			.prefill        (prefill),
			.os_en          (os_en),

			//.result_bus_o    (result_bus),
			.left_in_bus    (left_in_bus),
			.top_in_bus     (top_in_bus),
			.bottom_out_bus (bottom_out_bus),
			.right_out_bus  (right_out_bus)
		);

	task init();
		result1     <= 16'd0;
		result2     <= 16'd0;
		result3     <= 16'd0;
		result4     <= 16'd0;

		prefill     <= 1'b0;
		os_en       <= 1'b0;

		left_in_bus <= 32'd0;
		top_in_bus  <= 32'd0;
	endtask

	task os_test1();
		prefill     <= 1'b0;
		os_en       <= 1'b1;

		left_in_bus <= {16'd0,16'd1};
		top_in_bus  <= {16'd0,16'd5};
	endtask : os_test1

	task os_test2();
		prefill     <= 1'b0;
		os_en       <= 1'b1;

		left_in_bus <= {16'd3,16'd2};
		top_in_bus  <= {16'd6,16'd7};
	endtask : os_test2

	task os_test3();
		prefill     <= 1'b0;
		os_en       <= 1'b1;

		left_in_bus <= {16'd4,16'd0};
		top_in_bus  <= {16'd8,16'd0};
	endtask : os_test3

	task ws_test1();
		prefill    <= 1'b1;
		os_en      <= 1'b0;
	    left_in_bus <= {16'd0,16'd0};
		top_in_bus  <= {16'd8,16'd7};
	endtask : ws_test1

	task ws_test2();
		prefill    <= 1'b1;
		os_en      <= 1'b0;
	    left_in_bus <= {16'd0,16'd0};
		top_in_bus  <= {16'd6,16'd5};
	endtask : ws_test2

	task ws_test3();
		prefill    <= 1'b0;
		os_en      <= 1'b0;
	    left_in_bus <= {16'd0,16'd1};
		top_in_bus  <= {16'd0,16'd0};
	endtask : ws_test3

	task ws_test4();
		prefill    <= 1'b0;
		os_en      <= 1'b0;
	    left_in_bus <= {16'd2,16'd3};
		top_in_bus  <= {16'd0,16'd0};
	endtask : ws_test4

	task ws_test5();
		prefill    <= 1'b0;
		os_en      <= 1'b0;
	    left_in_bus <= {16'd4,16'd0};
		top_in_bus  <= {16'd0,16'd0};
	endtask : ws_test5

	task ws_test6();
		prefill    <= 1'b0;
		os_en      <= 1'b0;
	    left_in_bus <= {16'd0,16'd0};
		top_in_bus  <= {16'd0,16'd0};
	endtask : ws_test6

	random_dnn test;
	task random_test();
		//运算次数
		repeat(10) begin
			$display("============================================BEGIN================================================= ");
			//随机出输入与权重矩阵
			test = new();
			$display("\t input1 = %d \t  input2 = %d \t ", test.input1,test.input2);
			$display("\t input3 = %d \t  input4 = %d \t", test.input3,test.input4);

			$display("\t weight5 = %d \t  weight6 = %d \t ", test.weight1,test.weight2);
			$display("\t weight7 = %d \t  weight8 = %d \t", test.weight3,test.weight4);

			result1 = test.input1 * test.weight1 + test.input2 * test.weight3;
			result2 = test.input1 * test.weight2 + test.input2 * test.weight4;
			result3 = test.input3 * test.weight1 + test.input4 * test.weight3;
			result4 = test.input3 * test.weight2 + test.input4 * test.weight4;

			$display("\t result1 = %d \t  result2 = %d \t ", result1,result2);
			$display("\t result3 = %d \t  result4 = %d \t", result3,result4);
			$display("============================================================================================= ");

			//随机错误类型
			error_type = test.error_type;
			if (error_type == 2'b01) begin//input error
				$display("\t ERROR TYPE : INPUT ERROR \t");
				actual_input1 = test.input1 + 1;
				actual_input2 = test.input2;
				actual_input3 = test.input3;
				actual_input4 = test.input4;

				actual_weight1 = test.weight1;
				actual_weight2 = test.weight2;
				actual_weight3 = test.weight3;
				actual_weight4 = test.weight4;

			end else if(error_type == 2'b10) begin //weight error
				$display("\t ERROR TYPE : WEIGHT ERROR \t");
				actual_input1 = test.input1;
				actual_input2 = test.input2;
				actual_input3 = test.input3;
				actual_input4 = test.input4;

				actual_weight1 = test.weight1+1;
				actual_weight2 = test.weight2;
				actual_weight3 = test.weight3;
				actual_weight4 = test.weight4;
			end else if(error_type == 2'b11) begin //output error
				$display("\t ERROR TYPE : OUTPUT ERROR \t");
				actual_input1 = test.input1;
				actual_input2 = test.input2;
				actual_input3 = test.input3;
				actual_input4 = test.input4;

				actual_weight1 = test.weight1;
				actual_weight2 = test.weight2;
				actual_weight3 = test.weight3;
				actual_weight4 = test.weight4;
			end else begin
				$display("\t ERROR TYPE : NO ERROR \t");
				actual_input1 = test.input1;
				actual_input2 = test.input2;
				actual_input3 = test.input3;
				actual_input4 = test.input4;

				actual_weight1 = test.weight1;
				actual_weight2 = test.weight2;
				actual_weight3 = test.weight3;
				actual_weight4 = test.weight4;
			end

			//阶段1 缓存权重7、8
			prefill    <= 1'b1;
			os_en      <= 1'b0;
	    	left_in_bus <= {16'd0,16'd0};
			top_in_bus  <= {actual_weight3,actual_weight4};
			repeat(1)@(posedge clk);
			//阶段2 缓存权重5、6
			prefill    <= 1'b1;
			os_en      <= 1'b0;
	    	left_in_bus <= {16'd0,16'd0};
			top_in_bus  <= {actual_weight1,actual_weight2};
			repeat(1)@(posedge clk);
			//阶段3 输入数据1、2
			prefill    <= 1'b0;
			os_en      <= 1'b0;
	    	left_in_bus <= {16'd0,actual_input1};
			top_in_bus  <= {16'd0,16'd0};
			repeat(1)@(posedge clk);
			//阶段3 输入数据1、2
			prefill    <= 1'b0;
			os_en      <= 1'b0;
	    	left_in_bus <= {actual_input2,actual_input3};
			top_in_bus  <= {16'd0,16'd0};
			repeat(1)@(posedge clk);
			//阶段4 输入数据3、4
			prefill    <= 1'b0;
			os_en      <= 1'b0;
	    	left_in_bus <= {actual_input4,16'd0};
			top_in_bus  <= {16'd0,16'd0};
			repeat(1)@(posedge clk);
			//阶段5 输入数据3、4
			prefill    <= 1'b0;
			os_en      <= 1'b0;
	    	left_in_bus <= {16'd0,16'd0};
			top_in_bus  <= {16'd0,16'd0};
			actual_result2     <= bottom_out_bus[15:0];
			repeat(1)@(posedge clk);
			prefill    <= 1'b0;
			os_en      <= 1'b0;
	    	left_in_bus <= {16'd0,16'd0};
			top_in_bus  <= {16'd0,16'd0};
			actual_result1     <= bottom_out_bus[31:16];
			actual_result4     <= bottom_out_bus[15:0];
			repeat(1)@(posedge clk);
			prefill    <= 1'b0;
			os_en      <= 1'b0;
	    	left_in_bus <= {16'd0,16'd0};
			top_in_bus  <= {16'd0,16'd0};
			actual_result3     <= bottom_out_bus[31:16];
			repeat(5)@(posedge clk);

			$display("\t actual_input1 = %d \t   actual_input2 = %d \t ", actual_input1,actual_input2);
			$display("\t actual_input3 = %d \t   actual_input4 = %d \t ", actual_input3,actual_input4);

			$display("\t actual_weight5 = %d \t  actual_weight6 = %d\t ", actual_weight1,actual_weight2);
			$display("\t actual_weight7 = %d \t  actual_weight8 = %d\t ", actual_weight3,actual_weight4);
			//$display("============================================================================================= ");


			if (error_type == 2'b11) begin
				//随机输出错误
				error_flag = test.error;
				if (error_flag <= 2) begin
					//$display("\t error flag = %d",error_flag);
					$display("\t RESULT1 ERROR \t");
					$display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1+1,actual_result2);
					$display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
					// $display("\t Correct \t");
					// $display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					// $display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
				end else if (error_flag > 2 && error_flag <= 4) begin
					//$display("\t error flag = %d",error_flag);
					$display("\t RESULT2 ERROR \t");
					$display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2+1);
					$display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
					// $display("\t Correct \t");
					// $display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					// $display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
				end else if (error_flag > 4 && error_flag <= 6) begin
					//$display("\t error flag = %d",error_flag);
					$display("\t RESULT3 ERROR \t");
					$display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					$display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3+1,actual_result4);
					// $display("\t Correct \t");
					// $display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					// $display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
				end else if (error_flag > 6 && error_flag <= 8) begin
					//$display("\t error flag = %d",error_flag);
					$display("\t RESULT4 ERROR \t");
					$display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					$display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4+1);
					// $display("\t Correct \t");
					// $display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					// $display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
				end else begin
					// $display("\t error flag = %d",error_flag);
					$display("\t RESULT ALL CORRECT !!! \t");
					$display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					$display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
				end
			end else begin
					$display("\t actual_result1 = %d \t  actual_result2 = %d \t ", actual_result1,actual_result2);
					$display("\t actual_result3 = %d \t  actual_result4 = %d \t", actual_result3,actual_result4);
			end
			
			$display("============================================END================================================= ");
		end
	endtask : random_test


	initial begin
		init();
		repeat(3)@(posedge clk);
		/*test os*/
		os_test1();
		repeat(1)@(posedge clk);
		os_test2();
		repeat(1)@(posedge clk);
		os_test3();
		repeat(3)@(posedge clk)
		/*test ws*/
		ws_test1();
		repeat(1)@(posedge clk);
		ws_test2();
		repeat(1)@(posedge clk);
		ws_test3();
		repeat(1)@(posedge clk);
		ws_test4();
		repeat(1)@(posedge clk);
		ws_test5();
		repeat(1)@(posedge clk);
		ws_test6();
		repeat(2)@(posedge clk);
		repeat(1)@(posedge clk);

		// random_test();
		repeat(5)@(posedge clk);
		$finish;
	end

//iverilog 使用
	initial begin
	$dumpfile("wave_sa.vcd");  			// 指定VCD波形文件的名字为wave.vcd，仿真信息将记录到此文件，wave.vcd文件将存储在当前目录下
	//$dumpfile("./simulation/wave.vcd");  	// wave.vcd文件将存储在当前目录下的simulation文件夹下
	$dumpvars; // Dump所有层次的信号
	// $dumpvars(0, tb_systolic_array );  				// 指定层次数为0，则tb模块及其下面各层次的所有信号将被记录，我们需要所有信号都被记录
	#3000000 $finish;						// 一定要设置一个仿真停止时间
	end

endmodule
