# Shalgham-Choqondar :: Network Project :: Fall

## Overview
This project is a network-based messaging server implemented in Python. It allows users to sign up, log in, and communicate with each other in chat rooms. The server handles multiple client connections and ensures non-blocking operations using the `selectors` module.

## Features
- **User Management**: Sign up and log in functionality.
- **Chat Rooms**: Users can create and join chat rooms to communicate.
- **Non-blocking Server**: Handles multiple client connections without blocking.

## Non-Blocking Method
The server uses Python's `selectors` module to handle multiple connections efficiently. Here's a brief explanation of how the non-blocking method is implemented:

0. **Initialization**:
   ```python
   self.selector = selectors.DefaultSelector()
   self.selector.register(self.server, selectors.EVENT_READ, self.accept)

1. **Event Loop**:
The `non_blocking_server_listener` method runs an event loop that waits for events on registered file descriptors.

   ```python
   def non_blocking_server_listener(self):
       while not self.end:
           events = self.selector.select(timeout=None)
           for key, mask in events:
               callback = key.data
               callback(key.fileobj)
    ```
2. **Handling Connections**:

* **Accepting Connections**: When a new connection is detected, the accept method is called to accept the connection and register the client socket for reading.

  ```python
  def accept(self, server_socket):
      client, address = server_socket.accept()
      client.setblocking(False)
      self.selector.register(client, selectors.EVENT_READ, self.read)
  ```
* **Reading Data**: When data is available to read from a client socket, the read method is called to read the data, process it, and send a response.

  ```python
  def read(self, client):
      try:
          message = client.recv(BUFF_SIZE).decode("ascii")
          if message:
              handler, args = CommandHandler.parse(message)
              response: Response = handler(self, args, client)
              self.send_response_to_client(client, response)
          else:
              self.selector.unregister(client)
              client.close()
      except Exception as e:
          self.selector.unregister(client)
          client.close()
## Usage
1- **Start the Server**:

  ```python
  if __name__ == "__main__":
      server = MessengerServer()
      server.non_blocking_server_listener()
      server.server.close()
  ```
2- **Sign Up and Log In**:

* Call the signup method with a username and password.
* Call the login method with a username and password to get a session ID.

3- **Send Messages**:

* Use the `send_message` method to send messages to other users within a chat room.

## Dependencies
* Python 3.x
* `selectors` module (standard library)
* `passlib` for password hashing
* `hashlib`, `binascii`, `socket`, `json`, `logging`, `os` (standard libraries)

## Conclusion
This project demonstrates a non-blocking server architecture using Python's selectors module, allowing for efficient handling of multiple client connections in a network messaging application.
