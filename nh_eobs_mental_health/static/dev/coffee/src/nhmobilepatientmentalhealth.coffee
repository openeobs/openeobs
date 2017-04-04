# NHMobilePatient contains utilities for working with
# the nh_eobs_mobile patient view, namely getting data
#  and passing it to graph lib
### istanbul ignore next ###
class NHMobilePatientMentalHealth extends NHMobilePatient

  constructor: () ->
    super(refused=true, partialType="character")
    self = @
    rapidTranqButton = document.getElementById('toggle-rapid-tranq')
    rapidTranqButton.addEventListener("click", (e) ->
      self.handle_event(e, self.checkRapidTranqStatus, true, [self])
    )
    document.addEventListener("confirm_change", (e) ->
      self.handle_event(e, self.submitRapidTranqChange, true, [self])
    )

  getEndpoint: (self) ->
    rapidTranqButton = document.getElementById('toggle-rapid-tranq')
    intendedState = rapidTranqButton.getAttribute('data-state-to-set')
    intendedStateString = '?check='+intendedState.toString()
    dataId = document.getElementById("graph-content").getAttribute("data-id")
    url = self.urls.rapid_tranq(dataId)
    url.url += intendedStateString
    return {
      url: url,
      data: intendedStateString
    }

  checkRapidTranqStatus: (event, self) ->
    endpoint = self.getEndpoint(self)
    Promise.when(self.process_request('GET', endpoint.url.url, endpoint.data))
    .then((serverResult) ->
      body = document.getElementsByTagName("body")[0]
      result = serverResult[0]
      buttons = []
      if result.status is "fail"
        buttons = ["<a href=\"#\" data-action=\"close_reload\" "+
        "data-target=\"rapid_tranq_check\">Reload</a>"]
      else
        buttons = [
          "<a href=\"#\" data-action=\"close\" "+
          "data-target=\"rapid_tranq_check\">Cancel</a>",
          "<a href=\"#\" data-action=\"confirm_submit\" " +
          "data-target=\"rapid_tranq_check\">Confirm</a>"]
      return new NHModal(
        'rapid_tranq_check',
        result.title,
        '<p>' + result.desc + '</p>',
        buttons,
        0,
        body
      )
    )

  submitRapidTranqChange: (event, self) ->
    if not event.handled
      endpoint = self.getEndpoint(self)
      Promise.when(self.process_request(
        'POST', endpoint.url.url, endpoint.data))
      .then((serverResult) ->
        result = serverResult[0]
        body = document.getElementsByTagName("body")[0]
        newStatus = result.data.rapid_tranq
        rapidTranqButton = document.getElementById('toggle-rapid-tranq')
        rapidTranqButton.setAttribute('data-state-to-set', !newStatus)
        if newStatus is true
          rapidTranqButton.innerText = 'Stop Rapid Tranquilisation'
          rapidTranqButton.classList.remove('dont-do-it')
          rapidTranqButton.classList.add('white-on-black')
        else
          rapidTranqButton.innerText = 'Start Rapid Tranquilisation'
          rapidTranqButton.classList.add('dont-do-it')
          rapidTranqButton.classList.remove('white-on-black')
      )

### istanbul ignore if ###
if !window.NH
  window.NH = {}
### istanbul ignore else ###
window?.NH.NHMobilePatient = NHMobilePatientMentalHealth