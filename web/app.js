'use strict';

const canvas = document.getElementById('drawCanvas');
const context = canvas.getContext('2d');

const clearButton =
  document.getElementById('clearButton');

const classifyButton =
  document.getElementById('classifyButton');

const connectionStatus =
  document.getElementById('connectionStatus');

const statusDot =
  document.getElementById('statusDot');

const prediction =
  document.getElementById('prediction');

const resultMessage =
  document.getElementById('resultMessage');

let drawing = false;
let connected = false;


function resetCanvas() {
  context.fillStyle = '#000000';

  context.fillRect(
    0,
    0,
    canvas.width,
    canvas.height
  );

  context.strokeStyle = '#ffffff';
  context.lineWidth = 18;
  context.lineCap = 'round';
  context.lineJoin = 'round';

  prediction.textContent = 'A aguardar';

  resultMessage.textContent = connected
    ? 'Desenha uma seta e classifica.'
    : 'Liga ao ROS e desenha uma seta.';
}


function getPoint(event) {
  const rectangle =
    canvas.getBoundingClientRect();

  return {
    x:
      (event.clientX - rectangle.left)
      * canvas.width
      / rectangle.width,

    y:
      (event.clientY - rectangle.top)
      * canvas.height
      / rectangle.height,
  };
}


canvas.addEventListener(
  'pointerdown',
  (event) => {
    drawing = true;

    canvas.setPointerCapture(
      event.pointerId
    );

    const point = getPoint(event);

    context.beginPath();

    context.moveTo(
      point.x,
      point.y
    );
  }
);


canvas.addEventListener(
  'pointermove',
  (event) => {
    if (!drawing) {
      return;
    }

    const point = getPoint(event);

    context.lineTo(
      point.x,
      point.y
    );

    context.stroke();
  }
);


function stopDrawing() {
  drawing = false;
  context.closePath();
}


canvas.addEventListener(
  'pointerup',
  stopDrawing
);

canvas.addEventListener(
  'pointercancel',
  stopDrawing
);

canvas.addEventListener(
  'pointerleave',
  stopDrawing
);

clearButton.addEventListener(
  'click',
  resetCanvas
);


const ros = new ROSLIB.Ros({
  url: 'ws://localhost:9090',
});


const canvasTopic = new ROSLIB.Topic({
  ros: ros,
  name: '/vision/canvas_png',
  messageType: 'std_msgs/msg/String',
});


const commandTopic = new ROSLIB.Topic({
  ros: ros,
  name: '/vision/command',
  messageType: 'std_msgs/msg/String',
});


ros.on(
  'connection',
  () => {
    connected = true;

    connectionStatus.textContent =
      'Ligado ao ROS';

    statusDot.className =
      'dot online';

    classifyButton.disabled = false;

    resultMessage.textContent =
      'Desenha uma seta e classifica.';
  }
);


function markDisconnected(message) {
  connected = false;

  connectionStatus.textContent =
    'Desligado';

  statusDot.className =
    'dot offline';

  classifyButton.disabled = true;

  resultMessage.textContent = message;
}


ros.on(
  'error',
  () => markDisconnected(
    'Erro na ligação WebSocket.'
  )
);

ros.on(
  'close',
  () => markDisconnected(
    'Ligação ao ROS encerrada.'
  )
);


commandTopic.subscribe(
  (message) => {
    prediction.textContent =
      message.data;

    resultMessage.textContent =
      'Comando recebido: '
      + message.data;

    classifyButton.disabled = false;
  }
);


classifyButton.addEventListener(
  'click',
  () => {
    if (!connected) {
      return;
    }

    classifyButton.disabled = true;

    prediction.textContent = '...';

    resultMessage.textContent =
      'Imagem enviada. '
      + 'A aguardar classificação.';

    const pngDataUrl =
      canvas.toDataURL('image/png');

    const message =
      new ROSLIB.Message({
        data: pngDataUrl,
      });

    canvasTopic.publish(message);

    window.setTimeout(
      () => {
        if (
          prediction.textContent === '...'
        ) {
          classifyButton.disabled = false;

          resultMessage.textContent =
            'Sem resposta. '
            + 'Verifica os nós ROS.';
        }
      },
      5000
    );
  }
);


resetCanvas();
