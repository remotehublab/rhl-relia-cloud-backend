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

function TimeSink_NoiseSlide(val) {
          document.getElementById('textInput').value=val/100.0; 
          NoiseFactorTimeSink=val*(max_TimeSink_Re-min_TimeSink_Re)/100;
        }

function TimSinkZoomOutClick()
	{
	ZoomOutTimeSink=ZoomOutTimeSink+1 //i'm not very sure about this, but it may work.   
}  

function TimSinkZoomInClick()
	{
	ZoomInTimeSink=ZoomInTimeSink+1 //i'm not very sure about this, but it may work.   
}  

function TimSinkAutoScaleClick()
	{
	ZoomOutTimeSink=1 //i'm not very sure about this, but it may work.   
	ZoomInTimeSink=1 //i'm not very sure about this, but it may work.   
	
}  


function ReliaTimeSink (divIdentifier, deviceIdentifier, blockIdentifier) {
	var self = this;

        this.chart = new google.visualization.LineChart(document.getElementById(divIdentifier));

	this.url = window.API_BASE_URL + "data/current/" + deviceIdentifier + "/blocks/" + blockIdentifier;

	this.redraw = function() {

	var GridColor='#808080';
        	if($("#time-sink-grid-checkbox").is(':checked'))  {
        		GridColor = '#808080'; }
        	else { 
        		GridColor = '#ffffff'; }
        		
	var ZoomIn_factor;
        	if($("#time-sink-grid-checkbox").is(':checked'))  {
        		GridColor = '#808080'; }
        	else { 
        		GridColor = '#ffffff'; }
        		

	this.options = {
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
			viewWindow:{min:min_TimeSink_Re*(ZoomOutTimeSink/ZoomInTimeSink), max:max_TimeSink_Re*(ZoomOutTimeSink/ZoomInTimeSink)},
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
        	if($("#time-sink-real-checkbox").is(':checked'))  {
        		enableReal = true; }
        	else { 
        		enableReal = false; 
        		realData= new Array(realData.length).fill(null);
        	}
        		
			var enableImag;
        	if($("#time-sink-imag-checkbox").is(':checked'))  {
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
			
			var temp = document.getElementById("TimeSink_NumberOfPoints2Plot");
			var Number2plot=temp.value

			var randomArr = Array.from({length: Number2plot}, () => Math.random()*2-1);

			var timePerSample = 1000.0 / params.srate; // in milliseconds


			min_TimeSink_Re=realData[0];
			max_TimeSink_Re=realData[0];
			min_TimeSink_Im=imagData[0];
			max_TimeSink_Im=imagData[0];
			
			for (var pos = 0; pos < Number2plot	; ++pos) {
				var currentRow = [pos * timePerSample];
				if (enableReal){
					currentRow.push(realData[pos]+NoiseFactorTimeSink*randomArr[pos]);
					if(realData[pos] <min_TimeSink_Re)
						min_TimeSink_Re=realData[pos]; 
					if(realData[pos] >max_TimeSink_Re)
						max_TimeSink_Re=realData[pos] ;
				}
				if (enableImag)
					currentRow.push(imagData[pos]+NoiseFactorTimeSink*randomArr[pos]);
					if(imagData[pos] <min_TimeSink_Im)
						min_TimeSink_Im=imagData[pos]; 
					if(imagData[pos] >max_TimeSink_Im)
						max_TimeSink_Im=imagData[pos] ;

				formattedData.push(currentRow);
			}

			var dataTable = google.visualization.arrayToDataTable(formattedData);
			if( flagTimer=='pause')
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
