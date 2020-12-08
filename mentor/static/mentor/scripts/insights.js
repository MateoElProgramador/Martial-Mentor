
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
                alert(result.error_text);
            } else {  // Success
                userDetails = result.user_details
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
                alert(result.error_text);
            } else {  // Success
                sets = result.recent_sets
                user_gamertag = sets.gamerTag

                // Add sets content to page:
                populateRecentSets(sets);

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
                alert(result.error_text);
            } else {  // Success
                placements = result.placements
                populateRecentPlacements(placements);
            }
        }
    });
}


/** Populates recent sets card with content based on given JSON. */
function populateRecentSets(sets) {
    // Append each set result into the recent sets card:
    sets.sets.nodes.forEach(set => {
        if (set.displayScore != "DQ") {
            if (set.win == 'true') {
                $("#recent_sets_body").append('<p class="text-success">' + set.displayScore + '</p>');
            } else {
                $("#recent_sets_body").append('<p class="text-danger">' + set.displayScore + '</p>');
            }
        }
    });
}

/** Populates recent sets card with content based on given JSON. */
function populateRecentPlacements(placements) {
    // Append each set result into the recent sets card:
    placements.forEach(p => {
        $("#recent_placements_body").append('<div class="row my-2">\
            <div class="col-9">\
                <a href="http://www.smash.gg/' + p.slug + '/overview">' + p.tournament.name + '</a><br/>\
                <strong>' + p.standings.nodes[0].placement + nth(p.standings.nodes[0].placement) + '</strong> of ' + p.numEntrants + '\
            </div>\
            <div class="col-3">\
                <strong>(top ' + p.topPerc + '%)</strong>\
            </div>\
        </div>\
        ');
    });
}

/** Returns correct ordinal (e.g. 'th', 'st') of given number. Obtained from Stack Overflow:
    https://stackoverflow.com/questions/13627308/add-st-nd-rd-and-th-ordinal-suffix-to-a-number#answer-39466341 */
function nth(n) {
    return["st","nd","rd"][((n+90)%100-10)%10-1]||"th";
}