const dotenv = require('dotenv').config();

const http = require('http').createServer(handler); //require http server, and create server with function handler()
const fs = require('fs'); //require filesystem module
const io = require('socket.io-client');
const HX711 = require('pi-hx711');
const Gpio = require('pigpio').Gpio;

http.listen(8080); //listen to port 8080
	  console.log('running server file');

const socket = io(`http://${process.env.SERVER}:3000`, {
// const socket = io(`http://172.20.10.6:3000`, {
	// 172.20.10.6
    // reconnection: true,
    transports:['websocket'],
})

function handler (req, res) { //create server
  if (process.env.DEVICE_TYPE === 'gun') {
    socket.emit('shooting', process.env.PI_DEVICE_NUMBER);
  } else {
    socket.emit('hit', process.env.PI_DEVICE_NUMBER);
  }
  fs.readFile(__dirname + '/public/index.html', function(err, data) { //read file index.html in public folder
    if (err) {
      res.writeHead(404, {'Content-Type': 'text/html'}); //display 404 on error
      return res.end("404 Not Found");
    }
    res.writeHead(200, {'Content-Type': 'text/html'}); //write HTML
    res.write(data); //write data from index.html
    return res.end();
  });
}

	// MPU6050
	if (false) {
		const imu = new MPU6050();
		imu.initialize();

		console.log('device id: ', imu.getDeviceID());
		// use testConnection() to ensure the mpu6050 is working properly
		console.log('Device connected:', imu.testConnection());
		if (!imu.testConnection()){
			imu.reset();
					imu.initialize();
			console.log('reset');
			setTimeout(() => {}, 1000);
			console.log('device id: ', imu.getDeviceID());
			console.log('device i2c: ', imu.getDeviceI2CAddr());
			console.log('Device connected:', imu.testConnection());

		}
	}
	if(false){
		const intervalId = setInterval(() => {
			const motionData = imu.getMotionData();
			console.log('Device data:', motionData);
		}, 1000);
	}
	
		// HX711
		let ot = new Gpio(576, 'in'); // GPIO5
		let clk = new Gpio(577, 'in'); // GPIO6
		const loadcell = new HX711(6,5);
		loadcell.offset = 50000;
		loadcell.scale = 0.00001;
		
		
		const intervalId = setInterval(() => {
			const guageData = loadcell.read();
			console.log('strain data:', guageData);

		}, 1000);
	
 //GPIO
 
 if (false) {

  const Gpio = require('onoff').Gpio;
  let LED = new Gpio(575, 'out'); // GPIO4
  let maskDevice = new Gpio(577, 'in', 'rising',{debounceTimeout: 250}); //GPIO6
  let chestPlateDevice = new Gpio(587, 'in', 'rising',{debounceTimeout: 250}); //GPIO16
  let backPlateDevice = new Gpio(594, 'in', 'rising',{debounceTimeout: 250}); //GPIO23
  let gunDevice = new Gpio(585, 'in', 'rising',{debounceTimeout: 250}); //GPIO6=14


  const blinkLED = () => {

	LED.writeSync(1);
      setTimeout(() => {
        LED.writeSync(0);
      }, 1000);

  }

socket.on('connect_error', (error) => {
	console.log('error', error.message)
	console.log('error', error.code)

	console.log('error', error.description)
		console.log('error', error.context)

})



socket.on('connect', function () {
    console.log('connected to localhost:3000');
	  console.log('id', socket.id);

		
	
	  
    socket.emit('initializeDevice', process.env.DEVICE_TYPE, process.env.SWORD_NAME);
    
    if (process.env.DEVICE_TYPE !== 'sword') {
		let lightVal = 0;
		// Shot registering
		  maskDevice.watch(function (err, val) {
			console.log('mask_hit');
			if (err) {
			   console.error('There was an error', err);
			   return;
			}
			// if (process.env.DEVICE_TYPE === 'gun') {
			//   socket.emit('shooting', process.env.PI_DEVICE_NUMBER);
			// } else {
			  socket.emit('mask_hit', process.env.PI_DEVICE_NUMBER);
			  blinkLED();
			// }
		  });
		  chestPlateDevice.watch((err, val) => {
			console.log('chest hit');
			socket.emit('chest_hit', process.env.PI_DEVICE_NUMBER);
			blinkLED();
		  });
		  backPlateDevice.watch((err, val) => {
			console.log('back hit');
			socket.emit('back_hit', process.env.PI_DEVICE_NUMBER);
			blinkLED();
		  });
		  gunDevice.watch((err, val) => {
			console.log('shooting');
			socket.emit('shooting', process.env.PI_DEVICE_NUMBER);
			blinkLED();
		  })
		if (process.env.NODE_ENV === 'local') { //local test
		  setTimeout(()=> socket.emit('shooting', process.env.PI_DEVICE_NUMBER), 1500);
		}
		socket.on('hit', (data) => {
			console.log('message from the server:', data);
			socket.emit('serverEvent', "thanks server! for sending '" + data + "'");
			  if (process.env.NODE_ENV === 'pi') {
			  blinkLED();
			};
		});
	}
});
}

if (process.env.NODE_ENV === 'pi') {
  process.on('SIGINT', () => {
    LED.writeSync(0);
    LED.unexport();
    maskDevice.unexport();
    chestPlateDevice.unexport();
    backPlateDevice.unexport();
    gunDevice.unexport();
    process.exit();
  });
};
