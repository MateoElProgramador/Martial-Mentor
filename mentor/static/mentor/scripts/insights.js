
// When document ready:
$(function() {
    // Start chain of smashgg data requests (currently synchronous from each other):
    getUserDetails(user_slug, "player");
    getRecentSets(game_id, user_slug);
    //getRecentPlacements(user_slug, user_gamertag);
});


/** Sends Ajax request to obtain the gamertag of a user, given their user slug. */
function getUserDetails(user_slug, user_type, sets=null) {
    var user_gamertag = "";
    $.ajax({
      url: "/get-user-details/",
      type: 'POST',
      data: {user_slug: user_slug},
        success: function(response) {
            result = JSON.parse(response);
            // Call different success functions depending on querying player or opponent details:
            if (user_type == "player") {
                playerDetailsSuccess(result);
            } else {
                opponentDetailsSuccess(result, sets);
            }
        }
    });
}

/** Displays error message if player slug invalid, else populates title with gamertag and calls recent placements function. */
function playerDetailsSuccess(result) {
    if (result.error) {
        // Error
        alert('Error in user details! Please report this to admin.\n' + result.error_text);
        return;
    }

    // Success:
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

    // Get placements using Ajax:
    getRecentPlacements(user_slug, user_gamertag);
}


/** Sends Ajax request to obtain recent sets of player, given user slug and gamertag. */
function getRecentSets(game_id, user_slug, page_num=1, per_page=100, last_page=null, opponent_gamertag=null) {
    $.ajax({
      url: "/get-recent-sets/",
      type: 'POST',
      data: {game_id: game_id, user_slug: user_slug, page_num: page_num, per_page: per_page},
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

                user_gamertag = sets.gamerTag;

                // If this function was called by normal page loading and not for set history:
                if (page_num == 1) {
                    // Add sets content to page:
                    populateRecentSets(sets);

                    // Start off list of all sets:
                    allSets = sets.sets.nodes;

                    // Get set history if two user slugs have been entered in form:
                    if (opponent_slug != "") {
                        getAllSets(user_slug, user_gamertag, sets);
                    }
                    return;
                }


                // If called by set history:

                // Append new sets to allSets:
                allSets = allSets.concat(sets.sets.nodes);

                // TODO: check for start date being before game release.

                // If this is last batch of sets, send all sets to set history view:
                if (page_num == last_page) {
                    alert("Set num for this game: " + allSets.length);
                    getSetHistory(user_slug, user_gamertag, opponent_gamertag, allSets);
                }
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
function getSetHistory(user_slug, user_gamertag, opponent_gamertag, sets) {
    $.ajax({
      url: "/get-set-history/",
      type: 'POST',
      data: {game_id: game_id, user_slug: user_slug, opponent_slug: opponent_slug, user_gamertag: user_gamertag, opponent_gamertag: opponent_gamertag, sets: JSON.stringify(sets)},
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

                // Display set history in the card:
                populateSetHistory(setHistory);
            }
        }
    });
}


/** Get user details for opponent, with that success callback function calling the queries for all sets. */
function getAllSets(user_slug, user_gamertag, sets) {
    // Get opponent details via Ajax:
    getUserDetails(opponent_slug, "opponent", sets);
}


/** Display player and opponent gamertags in set history card, and request queries for entire set history of player,
    in batches to keep within smashgg query rate limits. Called on callback when opponent details have been obtained
    via Ajax. */
function opponentDetailsSuccess(result, sets) {
    if (result.error) {
        // Error
        alert('Error in opponent details! Please report this to admin.\n' + result.error_text);
        return;
    }

    // Success:
    oppDetails = result.user_details;

    // Show error message if error in query (almost definitely due to invalid player slug):
    if (oppDetails == 'null') {
        $('#set_history_body').append('<div id="set_history_error_text" class="set_history text-danger">Opponent slug does not exist</div>');
        return;
    }

    // Display player and opponent gamertags in set history card:
    opponent_gamertag = oppDetails.player.gamerTag;
    $("#set_history_title").html("Set History: " + user_gamertag + " vs " + opponent_gamertag);

    // get user details
    // get recent sets:
        // success:
            // if 2 slugs:
                // get opponent details:
                    // success:
                        // if slug is valid:
                            // Iteratively collate sets


    // Look at 'total' sets value from recent sets data
    // binSize = 100 (check this)
    // binNum = total / binSize
    // for i=0 to binNum:
        // get sets (pass i for page in query)
        // success callback:
            // Add sets to list in this scope (recent sets success callback, that is)
            // Populate recent sets card?
            // If date of last set is before release of videogame, or last bin:
                // Send all sets to set_history view to sort out

                // set_history success callback:
                    // Display set history

    // Split set queries into bins, depending on bin size and total number of sets:
    totalSetNum = sets.sets.pageInfo.total;
    binSize = 100;
    binNum = Math.ceil(totalSetNum / binSize);
    // alert("binNum: " + binNum);
    alert("Total sets: " + totalSetNum + "\nBin num: " + binNum);

    // Get all sets in several queries, with [binSize] sets from each query:
    for (var i=2; i<binNum+1; i++) {
        getRecentSets(game_id, user_slug, i, binSize, binNum, opponent_gamertag);
    }
}


/** Populates recent sets card with content based on given JSON. */
function populateRecentSets(sets) {
    $('#recent_sets_ratio').html("Recent win rate: " + sets.winCount + " out of " + sets.sets.nodes.length +
                                    " (" + Math.round((sets.winCount / sets.sets.nodes.length) * 100) + "%)");

    var lastTournament = "";

    // Append each set result into the recent sets card:
    sets.sets.nodes.every((set, i) => {
        var textClass = ""
        if (set.win == "true") {
            textClass = "text-success";
        } else {
            textClass = "text-danger";
        }

        var currTournament = set.event.tournament.name;

        // If first set, give value to lastTournament and add tournament header:
        if (i == 0) {
            lastTournament = currTournament;
            $("#recent_sets_body").append('<strong>' + currTournament + '</strong>');
        // If different tournament to previous sets, add horizontal rule and tournament header, update lastTournament:
        } else if (lastTournament != currTournament) {
            $("#recent_sets_body").append('<hr class="m-0 mb-1"/>');
            $("#recent_sets_body").append('<strong>' + currTournament + '</strong>');
            lastTournament = currTournament;
        }

        // Create row and columns for each recent set:
        $("#recent_sets_body").append('<div class="recent_set row my-2">\
            <div class="col-7">\
                <span class="' + textClass + '">' + set.displayScore + '</span>\
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

        // Create row and columns containing score, tournament and round:
        $("#set_history_body").append('<div class="set_history row my-2">\
            <div class="col-6">\
                <p class="'+ textClass + '">' + set.displayScore + '</p>\
            </div>\
            <div class="col-6">\
                <div>' + set.event.tournament.name + '</div>\
                <div><em>' + set.fullRoundText + '</em></div>\
            </div>\
        </div>\
        ');

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