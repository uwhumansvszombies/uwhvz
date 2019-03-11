function getTimeRemaining(endtime) {
  var t = Date.parse(endtime) - Date.parse(new Date());

  var seconds = Math.floor((t / 1000) % 60);
  var minutes = Math.floor((t / 1000 / 60) % 60);
  var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
  var days = Math.floor(t / (1000 * 60 * 60 * 24));

  return {
    'total': t,
    'days': days,
    'hours': hours,
    'minutes': minutes,
    'seconds': seconds
  };
}

function initClock(id, endtime) {
  var clock = document.getElementById(id);
  var days = clock.querySelector('#days');
  var hours = clock.querySelector('#hours');
  var minutes = clock.querySelector('#minutes');
  var seconds = clock.querySelector('#seconds');

  function updateClock() {
    var t = getTimeRemaining(endtime);
    
    days.innerHTML = ('0' + t.days);
    hours.innerHTML = ('0' + t.hours).slice(-2);
    minutes.innerHTML = ('0' + t.minutes).slice(-2);
    seconds.innerHTML = ('0' + t.seconds).slice(-2);

    if(t.total <= 0) {
      clearInterval(timeinterval);
    }
  }

  updateClock();
  var timeInterval = setInterval(updateClock, 1000);
}

var deadline = 'Sun Mar 10 2019 23:59:59 GMT-0400 (Eastern Daylight Time)';
initClock('countdown', deadline);
