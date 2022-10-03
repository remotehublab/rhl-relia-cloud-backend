function Relia() {

}

function TimSinkPauseRun() { 
  if( flagTimer=='pause')
  {
    flagTimer='run';
    document.getElementById('PauseRun').value="Play";
  }
  else
  {
    flagTimer='pause';
    document.getElementById('PauseRun').value="Pause";
  }
  
}

function IncAverageCounter(vals){
	average_number=average_number+1;
}
	
function DecAverageCounter(vals){
	average_number=average_number-1;
	if (average_number<1){
		average_number=1;
	}
}
	

function ReliaTimeSink (divIdentifier, deviceIdentifier, blockIdentifier) {
	var self = this;

	self.$div = $("#" + divIdentifier);

	self.$div.html(
	    "<div class=\"time-chart\" style=\"width: 900px; height: 500px\"></div>\n" +
	    "<div class=\"Checkbox_TimeSink_OnOffSignal\">" +
	        "<input type=\"checkbox\" class=\"checkbox time-sink-grid-checkbox\" checked> Grid<br>" +
	        "<input type=\"checkbox\" class=\"checkbox time-sink-real-checkbox\" checked> Real<br>" +
	        "<input type=\"checkbox\" class=\"checkbox time-sink-imag-checkbox\" checked> Imag<br>" +
		"<br>" + 

	        "<input type=\"submit\" name=\"checkout\" class=\"button zoom-in-button\" value=\"Zoom In\"> <br>" +
	        "<input type=\"submit\" name=\"checkout\" class=\"button zoom-out-button\" value=\"Zoom Out\"> <br>" +
	        "<input type=\"submit\" name=\"checkout\" class=\"button autoscale-button\" value=\"Zoom AutoScale\"> <br>" +
		"<br>" + 
		"<p>Add Noise</p>" +
	        //"<input type=\"range\" min=\"0\" max=\"100\" value=\"1\" onchange=\"TimeSink_NoiseSlide(this.value)\" <br>" +
	        "<input class=\"noise-slider\" type=\"range\" min=\"0\" max=\"100\" value=\"0\">" +
		"<p class=\"noise-slider-value\" value=\"1\"></p> <br>" +
		"<br>" + 
	        //"<input type=\"button\" id=\"PauseRun\" value=\"Pause\" onClick=\"TimSinkPauseRun()\" <br>" +
			//"<input type=\"button\" id=\"myButton1\" onClick=\"if(this.value=='Run') { this.value='Pause'; } else { this.value='Run'; }\" value=\"Pause\" <br>" +
			//"<input type=\"button\" id=\"myButton1\" onClick=RunPausePressed(this) <br>" +
		
		"<form>" +
		"  <select class=\"TimeSink_NumberOfPoints2Plot\">" + 
		"    <option value=\"1024\"selected=\"selected\">1024 points</option>" + 
		"    <option value=\"64\" >64 points</option>" + 
		"    <option value=\"128\">128 points</option>" + 
		"    <option value=\"256\">256 points</option>" + 
		"    <option value=\"512\">512 points</option>" + 
		"    <option value=\"2048\">2048 points</option>" + 
		"    <option value=\"4096\">4096 points</option>" + 
		"  </select>" + 
		"</form>" +
	    "</div>"
	);
	
	var $constChartDiv = self.$div.find(".time-chart");
	self.$gridCheckbox = self.$div.find(".time-sink-grid-checkbox");
	self.$timesinkrealCheckbox = self.$div.find(".time-sink-real-checkbox");
	self.$timesinkimagCheckbox = self.$div.find(".time-sink-imag-checkbox");
	self.$nop2plot = self.$div.find(".TimeSink_NumberOfPoints2Plot");
	
	self.maxTimeSinkRe=1;
	self.minTimeSinkRe=1;
	self.zoomInTimeSink=1;
        self.zoomOutTimeSink=1;

	self.$div.find(".zoom-in-button").click(function() {
		self.zoomInTimeSink += 1;
	});
	self.$div.find(".zoom-out-button").click(function() {

		self.zoomOutTimeSink += 1;
	});
	self.$div.find(".autoscale-button").click(function() {
		self.zoomInTimeSink = 1;
		self.zoomOutTimeSink = 1;
	});

	self.noiseFactor = 0;
	self.$timeSinkNoiseSlider = self.$div.find(".noise-slider"); // <input>
	self.$timeSinkNoiseSliderValue = self.$div.find(".noise-slider-value"); // <p>

	self.changeTimeSinkNoiseSlider = function () {
		self.$timeSinkNoiseSliderValue.text(self.$timeSinkNoiseSlider.val());
  		self.noiseFactor = self.$timeSinkNoiseSlider.val()*(self.maxTimeSinkRe-self.minTimeSinkRe)/100;
	};
	self.changeTimeSinkNoiseSlider();

	self.$timeSinkNoiseSlider.change(self.changeTimeSinkNoiseSlider);
	
	self.$flagPauseRun="Run";

	self.$TimeSinkPauseButton = document.getElementById("myButton1");	

	function RunPausePressed(el){
		if (el.value=='Pause') self.$flagPauseRun='Run';
		if (el.value=='Run') self.$flagPauseRun='Pause';
	}
	


	self.chart = new google.visualization.LineChart($constChartDiv[0]);

	self.url = window.API_BASE_URL + "data/current/" + deviceIdentifier + "/blocks/" + blockIdentifier;

	self.redraw = function() {

		var GridColor='#808080';
			if(self.$gridCheckbox.is(':checked'))  {
				GridColor = '#808080'; }
			else { 
				GridColor = '#ffffff'; }
				
	/*	var ZoomIn_factor;
			if($("#time-sink-grid-checkbox").is(':checked'))  {
				GridColor = '#808080'; }
			else { 
				GridColor = '#ffffff'; }/**/
				

		self.options = {
			title: 'Time',
			curveType: 'function',
			legend: { position: 'bottom' },
			hAxis: {
				title: 'Time (milliseconds)',
				gridlines: {
				color: GridColor,
			}
			},
			vAxis: {
				viewWindow:{
					min: self.minTimeSinkRe*(self.zoomOutTimeSink/self.zoomInTimeSink),
					max: self.maxTimeSinkRe*(self.zoomOutTimeSink/self.zoomInTimeSink)
				},
				title: 'Amplitude',
				gridlines: {
				color: GridColor,
			}
	       },
		explorer: {
			actions: ['dragToZoom', 'rightClickToReset'],
			axis: 'horizontal',
			keepInBounds: true,
			maxZoomIn: 4.0,
		},
		colors: ['#e2431e', '#000000'],
		};
	
	
		$.get(self.url).done(function (data) {
			setTimeout(function () {
				self.redraw();
			});

			if (!data.success) {
				console.log("Error: " + data.message);
				return;
			}

			if (data.data == null) {
				console.log("No data");
				return;
			}

			var params = data.data.params;

			console.log(data.data.block_type);
			console.log(data.data.type);
			console.log(params);
			console.log(data.data.data);

			var realData = data.data.data.streams['0']['real'];
			
			var imagData = data.data.data.streams['0']['imag'];
			$.each(realData, function (pos, value) {
				realData[pos] = parseFloat(value);
			});
			$.each(imagData, function (pos, value) {
				imagData[pos] = parseFloat(value);
			});

			var enableReal;
        	if(self.$timesinkrealCheckbox.is(':checked'))  {
        		enableReal = true; }
        	else { 
        		enableReal = false; 
        		realData= new Array(realData.length).fill(null);
        	}
        		
			var enableImag;
        	if(self.$timesinkimagCheckbox.is(':checked'))  {
        		enableImag = true; }
        	else { 
        		enableImag = false; 
//        	 	imagData=Array(realData.length).fill(null);
        	 }
			if (!enableReal && !enableImag) {
				console.log("Error: activate real or imag");
				return;
			}
        		
			var columns = ["Point"];
		        self.options['series'] = {};

			var counter = 0;

			if (enableReal) {
				columns.push("Real");
				self.options.series[counter] = '#e2431e';
				counter++;
			}	
			if (enableImag) {
				columns.push("Imag");
				self.options.series[counter] = '#1c91c0';
			}

			console.log(self.options);

			var formattedData = [
				columns
			];
			
			var Number2plot = self.$nop2plot.val();
			var randomArr = Array.from({length: Number2plot}, () => Math.random()*2-1);

			var timePerSample = 1000.0 / params.srate; // in milliseconds


			self.minTimeSinkRe=realData[0];
			self.maxTimeSinkRe=realData[0];
			self.$min_TimeSink_Im=imagData[0];
			self.$max_TimeSink_Im=imagData[0];
			
			for (var pos = 0; pos < Number2plot	; ++pos) {
				var currentRow = [pos * timePerSample];
				if (enableReal){
					currentRow.push(realData[pos]+self.noiseFactor*randomArr[pos]);
					if(realData[pos] <self.minTimeSinkRe)
						self.minTimeSinkRe=realData[pos]; 
					if(realData[pos] >self.maxTimeSinkRe)
						self.maxTimeSinkRe=realData[pos] ;
				}
				if (enableImag)
					currentRow.push(imagData[pos]+self.noiseFactor*randomArr[pos]);
					if(imagData[pos] <self.$min_TimeSink_Im)
						self.$min_TimeSink_Im=imagData[pos]; 
					if(imagData[pos] >self.$max_TimeSink_Im)
						self.$max_TimeSink_Im=imagData[pos] ;

				formattedData.push(currentRow);
			}

			var dataTable = google.visualization.arrayToDataTable(formattedData);
			if( self.$flagPauseRun=='Run')
				self.chart.draw(dataTable, self.options);
		});
	};

}

function ReliaConstellationSink (divIdentifier, deviceIdentifier, blockIdentifier) {
	var self = this;

	self.$div = $("#" + divIdentifier);

	self.$div.html(
	    "<div class=\"const-chart\" style=\"width: 900px; height: 500px\"></div>\n" +
	    "<div class=\"Checkbox_ConstSink_OnOffSignal\">" +
	        "<input type=\"checkbox\" class=\"checkbox const-sink-grid-checkbox\" checked> Grid<br>" +
		"<br>" + 
		"<form>" +
		"  <select class=\"ConstSink_NumberOfPoints2Plot\">" + 
		"    <option value=\"16\"selected=\"selected\">16 points</option>" + 
		"    <option value=\"32\" >32 points</option>" + 
		"    <option value=\"64\">64 points</option>" + 
		"    <option value=\"128\">128 points</option>" + 
		"    <option value=\"256\">256 points</option>" + 
		"    <option value=\"512\">512 points</option>" + 
		"    <option value=\"1024\">1024 points</option>" + 
		"  </select>" + 
		"</form>" +
	    "</div>"
	);

	var $constChartDiv = self.$div.find(".const-chart");
	self.$gridCheckbox = self.$div.find(".const-sink-grid-checkbox");
	self.$nop2plot = self.$div.find(".ConstSink_NumberOfPoints2Plot");

        this.chart = new google.visualization.ScatterChart($constChartDiv[0]);

	this.url = window.API_BASE_URL + "data/current/" + deviceIdentifier + "/blocks/" + blockIdentifier;

	this.redraw = function() {
	
	var GridColor='#808080';
        	if(self.$gridCheckbox.is(':checked'))  {
        		GridColor = '#808080'; }
        	else { 
        		GridColor = '#ffffff'; }
        		
	var ZoomIn_factor;
        	if(self.$gridCheckbox.is(':checked'))  {
        		GridColor = '#808080'; }
        	else { 
        		GridColor = '#ffffff'; }
        		
	this.options = {
		title: 'Constellation Plot',
		pointSize: 3,
		curveType: 'function',
		legend: { position: 'bottom' },
		hAxis: {
			title: 'In - phase',
			gridlines: {
        		color: GridColor,
      		}
			
		},
		vAxis: {
			title: 'Quadrature',
			gridlines: {
        		color: GridColor,
      		}
        	},
        explorer: {
        	actions: ['dragToZoom', 'rightClickToReset'],
        	axis: 'horizontal',
        	keepInBounds: true,
        	maxZoomIn: 4.0,
        },
	};
	
	
		$.get(self.url).done(function (data) {
			setTimeout(function () {
				self.redraw();
			});

			if (!data.success) {
				console.log("Error: " + data.message);
				return;
			}

			if (data.data == null) {
				console.log("No data");
				return;
			}

			var params = data.data.params;

			console.log(data.data.block_type);
			console.log(data.data.type);
			console.log(params);
			console.log(data.data.data);

			var realData = data.data.data.streams['0']['real'];
			var imagData = data.data.data.streams['0']['imag'];
			$.each(realData, function (pos, value) {
				realData[pos] = parseFloat(value);
			});
			$.each(imagData, function (pos, value) {
				imagData[pos] = parseFloat(value);
			});

			var formattedData = [
				["", ""]
			];

			var Number2plot = self.$nop2plot.val();

			for (var pos = 0; pos < Number2plot; ++pos) {
				formattedData.push([ realData[pos], imagData[pos]]);
			}

			var dataTable = google.visualization.arrayToDataTable(formattedData);
			self.chart.draw(dataTable, self.options);
		});
	};

}

function ReliaVectorSink (divIdentifier, deviceIdentifier, blockIdentifier) {
	var self = this;

	var avg_counter=1;
	//let average_number=1;
	var avg_data=Array(1024).fill(0);

	self.$div = $("#" + divIdentifier);

	self.$div.html(
	    "<div class=\"const-chart\" style=\"width: 900px; height: 500px\"></div>\n" +
			"<input type=\"button\" id=\"Inc\" onClick=IncAverageCounter(this) value=\"average +\"<br>" +
			"<input type=\"button\" id=\"Inc\" onClick=DecAverageCounter(this) value=\"average -\"<br>" +
	    
	    "</div>"
	);

	var $constChartDiv = self.$div.find(".const-chart");


        this.chart = new google.visualization.LineChart($constChartDiv[0]);
	this.options = {
		title: 'Power Spectra',
		curveType: 'function',
		legend: { position: 'bottom' },
		hAxis: {
			title: 'KHz'
		},
		vAxis: {
			title: 'dB',
        	}
	};

	this.url = window.API_BASE_URL + "data/current/" + deviceIdentifier + "/blocks/" + blockIdentifier;

	this.redraw = function() {
		$.get(self.url).done(function (data) {
			setTimeout(function () {
				self.redraw();
			});

			if (!data.success) {
				console.log("Error: " + data.message);
				return;
			}

			if (data.data == null) {
				console.log("No data");
				return;
			}

			var params = data.data.params;

			/*console.log(data.data.block_type);
			console.log(data.data.type);
			console.log(params);
			console.log(avg_counter);/**/

			var realData = data.data.data.streams[0];
			
			if (avg_counter<average_number){
			
				avg_counter=avg_counter+1;
				for (var k=0; k<1024;++k){
					avg_data[k]+=parseFloat(realData[k]);
				}

			}
			else{
				console.log(average_number);			
				avg_counter=0;
				var formattedData = [
					["Point", "Frequency"]
					];

				for (var pos = 0; pos < realData.length; ++pos) {
					formattedData.push([ pos, avg_data[pos]]);
				}
				avg_data=Array(1024).fill(0);

				var dataTable = google.visualization.arrayToDataTable(formattedData);
				self.chart.draw(dataTable, self.options);
				}
		});
	};

}




