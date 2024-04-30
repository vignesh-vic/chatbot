$(document).ready(function () {

  // Toggle between Chatbot and Live Agent containers
  $(".chatbot").click(function () {
    $("#chat-widget-container").hide();
    $("#live-agent-container").show();
  });

  $(".agent").click(function () {
    $("#chat-widget-container").show();
    $("#live-agent-container").hide();
  });
  $("#chat-history").append(
    '<img class="bot" src="/static/images/bot.png" style="margin-right:5px" width="20px" height="20px" alt="Bot" /><div class="bot-message alert alert-primary" role="alert">Hello, I am a bot. How can I help you?</div>'
  );
  $("#send-message-icon").click(function () {
    $("#chat-form").submit();
  });
  $("#chat-form").submit(function (event) {
    event.preventDefault();
    var userInput = $("#user-input").val().trim();
    if (userInput === "") {
      return;
    }

    var userInput = $("#user-input").val();
    $("#user-input").val("");
    $("#chat-history").append(
      '<div class="user-message alert alert-secondary text-right" role="alert">' +
      userInput +
      "</div>"
    );

    $("#chat-history").append(

      '<div id="typing-indicator">' + '<img class="" src="/static/images/bot.png" style="margin-right:5px" width="20px" height="20px" alt="Bot" />' +
      '<div class="dot"></div>' +
      '<div class="dot"></div>' +
      '<div class="dot"></div>' +
      '</div>'
    );
    $("#chat-history").scrollTop($("#chat-history")[0].scrollHeight);

    $("#typing-indicator").show();

    $.ajax({
      type: "POST",
      url: "/",
      data: {
        user_input: userInput,
      },
      success: function (data) {
        $("#typing-indicator").remove();
        $("#chat-history").append(
          ' <img class="bot" src="/static/images/bot.png" style="margin-right:5px" width="20px" height="20px" alt="Bot" /><div class="bot-message alert alert-primary" role="alert">' +
          data +
          "</div>"
        );
        $("#chat-history").scrollTop($("#chat-history")[0].scrollHeight);
      },
    });
  });

  $("#chat-widget-toggle").click(function () {
    $("#chat-widget-container").toggle();
    $("#chat-widget-toggle").hide();

  });

  $("#chat-widget-container .close-button").click(function () {
    $("#chat-widget-container").hide();
    $("#chat-widget-toggle").show();

  });


  //live agent
  $("#user-history").append(
    '<div class="user alert alert-primary" role="alert">Hello, I am live Agent. How can I help you?</div>'
  );

  var socket = io.connect("http://localhost:6008"); // Connect to your Socket.IO server
   // Function to send message using Socket.IO
   function sendMessage(message) {
    socket.send(message); // Send the message to the server
}

// Handle sending message when send button is clicked
$("#sendUserMessage").click(function () {
    var userMessage = $("#user-message").val().trim();
    if (userMessage !== "") {
        sendMessage(userMessage); // Call the sendMessage function with the user's message
        $("#user-message").val(""); // Clear the input field after sending message
    }
});

// Handle sending message when enter key is pressed in the input field
$("#user-message").keypress(function (e) {
    if (e.which === 13) { 
        var userMessage = $("#user-message").val().trim();
        if (userMessage !== "") {
            sendMessage(userMessage); 
            $("#user-message").val(""); 
        }
        return false; // Prevent form submission
    }
});

// Handle receiving messages from the server
socket.on('message', function (data) {
    $("#user-history").append( 
      '<div class="user-message alert alert-secondary text-left" role="alert">' + data + '</div>'
  );   
    $("#user-history").scrollTop($("#user-history")[0].scrollHeight);
});

  // Handle closing the live agent container
  $("#live-agent-container .close-button").click(function () {
    $("#live-agent-container").hide();
    $("#chat-widget-toggle").show();
  });

});
