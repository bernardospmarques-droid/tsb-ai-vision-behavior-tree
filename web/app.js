'use strict';
const canvas = document.getElementById('drawCanvas');
const context = canvas.getContext('2d');
const clearButton = document.getElementById('clearButton');
const classifyButton = document.getElementById('classifyButton');
const squareButton = document.getElementById('squareButton');
const circleButton = document.getElementById('circleButton');
const connectionStatus = document.getElementById('connectionStatus');
const statusDot = document.getElementById('statusDot');
const prediction = document.getElementById('prediction');
const resultMessage = document.getElementById('resultMessage');
let drawing = false;
let connected = false;
function setActionButtons(enabled) {
  classifyButton.disabled = !enabled;
  squareButton.disabled = !enabled;
  circleButton.disabled = !enabled;
}
function resetCanvas() {
  context.fillStyle = '#000000';
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = '#ffffff';
  context.lineWidth = 18;
  context.lineCap = 'round';
  context.lineJoin = 'round';
  prediction.textContent = 'A aguardar';
  resultMessage.textContent = connected ? 'Desenha uma seta ou escolhe uma forma.' : 'Liga ao ROS e escolhe uma acao.';
}
function getPoint(event) {
  const rectangle = canvas.getBoundingClientRect();
  return {x: (event.clientX - rectangle.left) * canvas.width / rectangle.width,
          y: (event.clientY - rectangle.top) * canvas.height / rectangle.height};
}
canvas.addEventListener('pointerdown', (event) => {
  drawing = true; canvas.setPointerCapture(event.pointerId);
  const point = getPoint(event); context.beginPath(); context.moveTo(point.x, point.y);
});
canvas.addEventListener('pointermove', (event) => {
  if (!drawing) return; const point = getPoint(event); context.lineTo(point.x, point.y); context.stroke();
});
function stopDrawing() { drawing = false; context.closePath(); }
canvas.addEventListener('pointerup', stopDrawing);
canvas.addEventListener('pointercancel', stopDrawing);
canvas.addEventListener('pointerleave', stopDrawing);
clearButton.addEventListener('click', resetCanvas);
const ros = new ROSLIB.Ros({url: 'ws://localhost:9090'});
const canvasTopic = new ROSLIB.Topic({ros, name: '/vision/canvas_png', messageType: 'std_msgs/msg/String'});
const commandTopic = new ROSLIB.Topic({ros, name: '/vision/command', messageType: 'std_msgs/msg/String'});
ros.on('connection', () => {
  connected = true; connectionStatus.textContent = 'Ligado ao ROS'; statusDot.className = 'dot online';
  setActionButtons(true); resultMessage.textContent = 'Desenha uma seta ou escolhe uma forma.';
});
function markDisconnected(message) {
  connected = false; connectionStatus.textContent = 'Desligado'; statusDot.className = 'dot offline';
  setActionButtons(false); resultMessage.textContent = message;
}
ros.on('error', () => markDisconnected('Erro na ligacao WebSocket.'));
ros.on('close', () => markDisconnected('Ligacao ao ROS encerrada.'));
commandTopic.subscribe((message) => {
  prediction.textContent = message.data; resultMessage.textContent = 'Comando recebido: ' + message.data;
  if (connected) setActionButtons(true);
});
function publishShape(command) {
  if (!connected) return;
  commandTopic.publish(new ROSLIB.Message({data: command}));
  prediction.textContent = command;
  resultMessage.textContent = command === 'SQUARE'
    ? 'Quadrado enviado para a Behavior Tree: 4 repeticoes de UP + LEFT.'
    : 'Circulo enviado para a Behavior Tree: velocidades linear e angular simultaneas.';
}
squareButton.addEventListener('click', () => publishShape('SQUARE'));
circleButton.addEventListener('click', () => publishShape('CIRCLE'));
classifyButton.addEventListener('click', () => {
  if (!connected) return;
  setActionButtons(false); prediction.textContent = '...';
  resultMessage.textContent = 'Imagem enviada. A aguardar classificacao.';
  canvasTopic.publish(new ROSLIB.Message({data: canvas.toDataURL('image/png')}));
  window.setTimeout(() => {
    if (prediction.textContent === '...') {
      setActionButtons(true); resultMessage.textContent = 'Sem resposta. Verifica os nos ROS.';
    }
  }, 5000);
});
setActionButtons(false);
resetCanvas();
