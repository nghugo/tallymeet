from polloption.models import PollOption, PollOptionResponse

def getSavedPollPassword(requestSession, id):
    """ Objective: return the latest correct poll password the user provided for a poll id, and also save it under poll_id key of the entered_password_dict in the session object
        -------------------------------------------------------------------
        Priorities:
        1. returns self.request.session['pollPasswordAtPollCreation'] if exists
            (most recent password is set after creating poll)
            (required because the object (hence its id) would not have been created by that point)
            (hence, we can't set requestSession['entered_password_dict'][id] yet)
        2. else returns requestSession['entered_password_dict'][id] if exists
            (represents the latest correct poll password the user provided for a poll id)
        3. else returns empty string ("") 
            (represents None, we redirect but do not flash the "wrong password" message) """
    
    if 'entered_password_dict' not in requestSession:
        requestSession['entered_password_dict'] = {}  # maps id (str) -> password (str)
    entered_password_dict = requestSession.get('entered_password_dict')

    if 'pollPasswordAtPollCreation' in requestSession:
        entered_password_dict[id] = requestSession['pollPasswordAtPollCreation']  # mutate entered_password_dict to save the new password into the session object
        del requestSession['pollPasswordAtPollCreation']  # delete most recent password once used
    
    # explicit save -> by default, Django does not save to session DB after mutation, only addition or deletion of values
    # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
    requestSession.save()
    
    entered_password = entered_password_dict.get(id, "")
    return entered_password

def getSorted_OptionsResponsesList(poll):
    """ Given a particular poll, returns an object voting results.
    The object contains all poll options and associated counts of PREFER, YES, and NO
    
    The list looks like:
    [
        [Option 1, responses], 
        [Option 2, responses], 
        [Option 3, responses], 
        …
    ]

    Responses is a dictionary of 3 key-value pairs
    {
        PollOptionResponse.PREFER: ['john', 'jack'], 
        PollOptionResponse.YES: ['jane'], 
        PollOptionResponse.NO: ['mary'], 
    }
    
    """

    options = PollOption.objects.filter(poll_id = poll)
    optionsResponsesList = []   

    for option in options:
        responseToPeople = {PollOptionResponse.YES: [], PollOptionResponse.PREFER: [], PollOptionResponse.NO: []}
        for optionResponse in PollOptionResponse.objects.filter(poll_option_id = option):
            if optionResponse.response == PollOptionResponse.YES:
                responseToPeople[PollOptionResponse.YES].append(optionResponse.responder_name)
            elif optionResponse.response == PollOptionResponse.PREFER:
                responseToPeople[PollOptionResponse.PREFER].append(optionResponse.responder_name)
            else:
                responseToPeople[PollOptionResponse.NO].append(optionResponse.responder_name)
        optionsResponsesList.append([option, responseToPeople])

    # sort by YES+PREFER count (desc) then PREFER count (desc)
    optionsResponsesList.sort(
        key = lambda obj: (
            - len(obj[1][PollOptionResponse.YES]) - len(obj[1][PollOptionResponse.PREFER]),
            - len(obj[1][PollOptionResponse.PREFER])
        )
    )
        

    return optionsResponsesList

def addDenseRank(sortedOptionResponsesList):
    """ Given a particular sortedOptionResponsesList, 
    returns a version with dense rank appended to the end of each object
    
    The input looks like:
    [
        [Option 1, responses], 
        [Option 2, responses], 
        [Option 3, responses], 
        …
    ]

    The output looks like
    [
        [Option 1, responses, dense_rank], 
        [Option 2, responses, dense_rank], 
        [Option 3, responses, dense_rank], 
        …
    ]
    
    """
    rank = 1
    for i in range(len(sortedOptionResponsesList)):
        curr = sortedOptionResponsesList[i]
        prev = sortedOptionResponsesList[i-1] if i > 0 else None
        if i > 0 and (
            len(curr[1][PollOptionResponse.YES]) != len(prev[1][PollOptionResponse.YES])
            or len(curr[1][PollOptionResponse.PREFER]) != len(prev[1][PollOptionResponse.PREFER])
        ):
            rank += 1
        curr.append(rank)
    
    return sortedOptionResponsesList