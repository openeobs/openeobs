describe('Constructor', function(){
    it('attaches an event listener to each invite in the patient list', function(){
        // create test for one invite

        // create test for two invites

        // create test for no invites
    });
});

describe('Click handler', function(){
    it('Shows a modal with the list of patients', function(){
        // click the invitation
        // test that NHModal was called with the relevant information
    });
    it('Sends a request to the server on pressing Accept button in modal', function(){
        // click the invitation
        // test that NHModal was called with the relevant information
        // find the accept button
        // press the accept button
        // test that NHModal handles click event
        // test that NHMobileShareInvite handles the event
        // test that server is contacted with relevant information
    });
    it('Shows an error when the server is unable to complete the accept request', function(){
        // click the invitation
        // test that NHModal was called with the relevant information
        // find the accept button
        // press the accept button
        // test that NHModal handles click event
        // test that NHMobileShareInvite handles the event
        // test that server is contacted with relevant information
        // test that error message is shown on server returning an error
    });
});