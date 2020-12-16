
// When document ready:
$(function() {
    // Start chain of smashgg data requests (currently synchronous from each other):
    getUserDetails(user_slug);
    getRecentSets(game_id, user_slug);
    //getRecentPlacements(user_slug, user_gamertag);
});


/** Sends Ajax request to obtain the gamertag of a user, given their user slug. */
function getUserDetails(user_slug) {
    var user_gamertag = "";
    $.ajax({
      url: "/get-user-details/",
      type: 'POST',
      data: {user_slug: user_slug},
        success: function(response) {
            result = JSON.parse(response);
            if (result.error) {
                // Error
                alert('Error in user details! Please report this to admin.\n' + result.error_text);
            } else {  // Success
                userDetails = result.user_details

                // Show error message if error in query (almost definitely due to invalid player slug):
                if (userDetails == 'null') {
                    $('#recent_sets_body').append('<div id="slug_error_text_sets" class="text-danger">Player slug does not exist</div>');
                    $('#recent_placements_body').append('<div id="slug_error_text_placements" class="text-danger">Player slug does not exist</div>');
                    return;
                }

                user_gamertag = userDetails.player.gamerTag

                // Add newly acquired gamertag to heading:
                $("#gamertag_header").html(user_gamertag + "'s Stats");

                // Retrieve tournament placements, given newly obtained user gamertag:
                //getRecentSets(game_id, user_slug, user_gamertag);
                getRecentPlacements(user_slug, user_gamertag);
            }
        }
    });
}


/** Sends Ajax request to obtain recent sets of player, given user slug and gamertag. */
function getRecentSets(game_id, user_slug) {
    $.ajax({
      url: "/get-recent-sets/",
      type: 'POST',
      data: {game_id: game_id, user_slug: user_slug},
        success: function(response) {
            result = JSON.parse(response);
            if (result.error) {
                // Error
                alert('Error in recent sets! Please report this to admin.\n' + result.error_text);
            } else {  // Success
                sets = result.recent_sets

                // Exit function and avoid further processing and query calls, since player slug is invalid:
                if (sets == 'null') {
                    return;
                }

                user_gamertag = sets.gamerTag

                // Add sets content to page:
                populateRecentSets(sets);

                // Get set history if two user slugs have been entered in form:
                if (opponent_slug != "") {
                    getSetHistory(user_slug, user_gamertag, sets);
                }

                // Now get recent tournament placings async:
                //getRecentPlacements(user_slug, user_gamertag);
            }
        }
    });
}


/** Sends Ajax request to obtain recent tournament placements of a player, given their user slug and gamertag. */
function getRecentPlacements(user_slug, user_gamertag) {
    $.ajax({
      url: "/get-recent-placements/",
      type: 'POST',
      data: {game_id: game_id, user_slug: user_slug, user_gamertag: user_gamertag},
        success: function(response) {
            result = JSON.parse(response);
            if (result.error) {
                // Error
                alert('Error in recent placements! Please report this to admin.\n' + result.error_text);
            } else {  // Success
                placements = result.placements
                populateRecentPlacements(placements);
            }
        }
    });
}

/** Sends Ajax request to get set history between two players, given their user slugs. */
function getSetHistory(user_slug, user_gamertag, sets) {
    $.ajax({
      url: "/get-set-history/",
      type: 'POST',
      data: {game_id: game_id, user_slug: user_slug, opponent_slug: opponent_slug, user_gamertag: user_gamertag, sets: JSON.stringify(sets)},
        success: function(response) {
            result = JSON.parse(response);
            if (result.error) {
                // Error
                alert('Error in set history! Please report this to admin.\n' + result.error_text);
            } else {  // Success
                setHistory = result.set_history;

                // Display error message if opponent not found from slug:
                if (setHistory == 'null') {
                    $('#set_history_body').append('<div id="set_history_error_text" class="set_history text-danger">Opponent slug does not exist</div>');
                    return;
                }

                populateSetHistory(setHistory);
            }
        }
    });
}


/** Populates recent sets card with content based on given JSON. */
function populateRecentSets(sets) {
    $('#recent_sets_ratio').html("Recent win rate: " + sets.winCount + " out of " + sets.sets.nodes.length +
                                    " (" + Math.round((sets.winCount / sets.sets.nodes.length) * 100) + "%)");
    // Append each set result into the recent sets card:
    sets.sets.nodes.every((set, i) => {
        var textClass = ""
        if (set.win == "true") {
            textClass = "text-success";
        } else {
            textClass = "text-danger";
        }

        // Create row and columns for each recent set:
        $("#recent_sets_body").append('<div class="recent_set row my-2">\
            <div class="col-7">\
                <p class="recent_set ' + textClass + '">' + set.displayScore + '</p>\
            </div>\
            <div class="col-5">\
                <span class="row">' + set.fullRoundText + '</span>\
            </div>\
        </div>\
        ');

        // Only display the first 15 sets:
        if (i >= 14) { return false; }

        return true;
    });
}

/** Populates recent sets card with content based on given JSON. */
function populateRecentPlacements(placements) {
    // Append placements data into card:
    placements.forEach(p => {
        var standingsText = '';
        var percText = ''

        // Deal with tournaments with null standings accordingly:
        if (p.topPerc == 'null') {
            standingsText = 'N/A</strong> (No standings found)';
            percText = 'N/A'
        } else if (p.topPerc == 'did not compete') {
            standingsText = 'N/A</strong> (Did not compete)';
            percText = 'N/A';
        } else {
            standingsText = p.standings.nodes[0].placement + nth(p.standings.nodes[0].placement) + '</strong> of ' + p.numEntrants;
            percText = '<strong>(top ' + p.topPerc + '%)</strong>';
        }

        $("#recent_placements_body").append('<div class="recent_placing row my-2">\
            <div class="col-9">\
                <a href="http://www.smash.gg/' + p.slug + '/overview">' + p.tournament.name + '</a><br/>\
                <strong>' + standingsText + '\
            </div>\
            <div class="col-3">\
                ' + percText + '\
            </div>\
        </div>\
        ');
    });
}

/** Populates set history card with content based on given JSON. */
function populateSetHistory(sets) {

    $("#set_history_title").html("Set History: " + user_gamertag + " vs " + sets.opponentGamertag);
    $('#set_history_ratio').html("Recent win rate: " + sets.winCount + " out of " + sets.sets.length +
                                    " (" + Math.round((sets.winCount / sets.sets.length) * 100) + "%)");

    // Append each set result into the recent sets card:
    sets.sets.every((set, i) => {
        var textClass = ""
        if (set.win == "true") {
            textClass = "text-success";
        } else {
            textClass = "text-danger";
        }
        $("#set_history_body").append('<p class="set_history ' + textClass + '">' + set.displayScore + '</p>');

        // Only display the first 15 sets:
//        if (i >= 15) { return false; }

        return true;
    });
}

/** Returns correct ordinal (e.g. 'th', 'st') of given number. Obtained from Stack Overflow:
    https://stackoverflow.com/questions/13627308/add-st-nd-rd-and-th-ordinal-suffix-to-a-number#answer-39466341 */
function nth(n) {
    return["st","nd","rd"][((n+90)%100-10)%10-1]||"th";
}