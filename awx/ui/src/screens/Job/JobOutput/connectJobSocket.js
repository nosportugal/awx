let ws;

export default function connectJobSocket({ type, id }, onMessage) {
  const socket = new WebSocket(
    `${window.location.protocol === 'http:' ? 'ws:' : 'wss:'}//${
      window.location.host
    }${window.location.pathname}websocket/`
  );
  ws = socket;

  socket.onopen = () => {
    const xrftoken = `; ${document.cookie}`
      .split('; csrftoken=')
      .pop()
      .split(';')
      .shift();
    const eventGroup = `${type}_events`;
    socket.send(
      JSON.stringify({
        xrftoken,
        groups: { jobs: ['summary', 'status_changed'], [eventGroup]: [id] },
      })
    );
  };

  socket.onmessage = (e) => {
    onMessage(JSON.parse(e.data));
  };

  socket.onclose = (e) => {
    if (e.code !== 1000) {
      // eslint-disable-next-line no-console
      console.debug('Socket closed. Reconnecting...', e);
      setTimeout(() => {
        connectJobSocket({ type, id }, onMessage);
      }, 1000);
    }
  };

  socket.onerror = (err) => {
    // eslint-disable-next-line no-console
    console.debug('Socket error: ', err, 'Disconnecting...');
    socket.close();
  };
}

export function closeWebSocket() {
  if (ws) {
    ws.close();
  }
}
