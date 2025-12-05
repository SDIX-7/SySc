// import {SERVER_ADDRESS} from '../static/js/global'
import VueSocketIO from 'vue-socket.io'
import SocketIO from 'socket.io-client'

export const VUE_SOCKET_IO = new VueSocketIO({
  debug: true,
  connection: SocketIO('http://localhost:5000', {
    transports: ['websocket', 'polling'],
    autoConnect: false
  })
})
