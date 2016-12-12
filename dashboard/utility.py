from .models import WeekWarning


def check_warnings(team):
    status = {
        'green': 'G',
        'yellow': 'Y',
        'red': 'R'
    }

    current_week = team.dashboard.current_week
    try:
        week_warning = WeekWarning.objects.get(week_number=current_week)
        tw = team.warnings
    except WeekWarning.DoesNotExist:
        raise
    except team.RelatedObjectDoesNotExist:
        raise

    # Total calls check
    def _total_calls_check():
        response_count = team.consultant_surveys.all().count()
        change_count = team.team_status.call_change_count
        total_call_count = response_count + change_count
        if total_call_count < week_warning.calls_r:
            msg = "Total Calls ({0}+{1})={2} < Expected Calls Red: {3}"
            msg = msg.format(response_count, change_count, total_call_count,
                             week_warning.calls_r)
            return status['red'], msg
        elif total_call_count < week_warning.calls_y:
            msg = "Total Calls ({0}+{1})={2} < Expected Calls Yellow: {3}"
            msg = msg.format(response_count, change_count, total_call_count,
                             week_warning.calls_y)
            return status['yellow'], msg
        else:
            msg = "Total Calls ({0}+{1})={2} >= Expected Calls: " \
                  "Yellow:{3} and Red:{4}"
            msg = msg.format(response_count, change_count, total_call_count,
                             week_warning.calls_y, week_warning.calls_r)
            return status['green'], msg

    # Current Phase
    def _phase_check():
        last_response = team.last_response
        # If there are no responses skip the following section
        if last_response:
            current_phase = last_response.current_phase
            yellow = week_warning.phase_y
            red = week_warning.phase_r
            green = week_warning.phase
            if red:
                if current_phase.phase_number <= red.phase_number:
                    msg = "Current Phase:{0} < Red warning Phase:{1}"
                    msg = msg.format(current_phase, red)
                    return status['red'], msg

            if yellow:
                if yellow.phase_number == current_phase.phase_number:
                    msg = "Current Phase:{1} is Yellow warning Phase:{0}"
                    msg = msg.format(yellow, current_phase)
                    return status['yellow'], msg
            if green:
                if green.phase_number == current_phase.phase_number:
                    msg = "Current Phase:{1} is Expected Phase:{0}"
                    msg = msg.format(green, current_phase)
                    return status['green'], msg
        msg = "No consultant responses found!"
        return status['green'], msg

    # Kick Off
    def _kick_off_check():
        if team.team_status.kick_off == "NS":
            yellow = week_warning.kick_off_y
            red = week_warning.kick_off_r
            msg = "Kick off not yet happened"
            if yellow:
                return status['yellow'], msg
            if red:
                return status['red'], msg
            else:
                return status['green'], "No kick off warnings found for this " \
                                        "week. "
        return status['green'], "Kick off Done."

    # Mid Term
    def _mid_term_check():
        if team.team_status.mid_term == "NS":
            yellow = week_warning.mid_term_y
            red = week_warning.mid_term_r
            msg = "Mid Term not yet happened"
            if yellow:
                return status['yellow'], msg
            elif red:
                return status['red'], msg
            else:
                return status['green'], "No mid term warnings found for this " \
                                        "week. "
        return status['green'], "Mid Term Done"

    # Consultant Rating
    def _consultant_rating_check():
        c_last_rating = team.last_consultant_rating
        if c_last_rating:
            if c_last_rating <= week_warning.consultant_rating_r:
                msg = "Last Consultant Rating: {0} <= Consultant Rating " \
                      "Red Warning: {1}".format(c_last_rating,
                                                week_warning.consultant_rating_r)
                return status['red'], msg
            else:
                msg = "Last Consultant Rating: {0} > Consultant Rating " \
                      "Red Warning: {1}".format(c_last_rating,
                                                week_warning.consultant_rating_r)
                return status['green'], msg
        # If there are no ratings
        else:
            return status['green'], "No Rating found (Either there are no " \
                                    "consultant responses or none of the " \
                                    "consultant responses have rating value) "

    # Fellow Rating
    def _fellow_rating_check():
        f_last_rating = team.last_fellow_rating
        if f_last_rating:
            if f_last_rating < week_warning.fellow_rating_r:
                msg = "Last Fellow Rating: {0} < Fellow Rating " \
                      "Red Warning: {1}".format(f_last_rating,
                                                week_warning.fellow_rating_r)
                return status['red'], msg
            else:
                msg = "Fellow Rating: {0} > Fellow Rating " \
                      "Red Warning: {1}".format(f_last_rating,
                                                week_warning.fellow_rating_r)
                return status['green'], msg
        # If there are no ratings
        else:
            return status['green'], "No Rating found (Either there are no " \
                                    "fellow responses or none of the " \
                                    "fellow responses have rating value) "

    # Unprepared calls
    def _unprepared_calls_check():
        percentage = team.unprepared_calls_percentage
        if percentage:
            if percentage < week_warning.unprepared_calls_r:
                msg = "% Unprepared calls: {0} < % Unprepared Calls Red " \
                      "Threshold"
                msg = msg.format(percentage, week_warning.unprepared_calls_r)
                return status['red'], msg
            elif percentage < week_warning.unprepared_calls_y:
                msg = "% Unprepared calls: {0} < % Unprepared Calls Yellow " \
                      "Threshold"
                msg = msg.format(percentage, week_warning.unprepared_calls_y)
                return status['yellow'], msg
            else:
                msg = "% Unprepared calls: {0} > % Unprepared calls " \
                      "Threshold Yellow:{1} and Red:{2}"
                msg = msg.format(percentage, week_warning.unprepared_calls_y,
                                 week_warning.unprepared_calls_r)
                return status['green'], msg
        msg = ""
        if percentage is 0:
            msg = "% Unprepared calls: 0. Members were prepared for all " \
                  "the calls."
        if percentage is None:
            msg = "Could not calculate % Unprepared calls. " \
                  "No consultant responses found."

        return status['green'], msg
    tw.call_count, tw.call_count_comment = _total_calls_check()
    tw.phase, tw.phase_comment = _phase_check()
    tw.kick_off, tw.kick_off_comment = _kick_off_check()
    tw.mid_term, tw.mid_term_comment = _mid_term_check()
    tw.consultant_rating, tw.consultant_rating_comment = _consultant_rating_check()
    tw.fellow_rating, tw.fellow_rating_comment = _fellow_rating_check()
    tw.unprepared_call, tw.unprepared_call_comment = _unprepared_calls_check()
    tw.save()
