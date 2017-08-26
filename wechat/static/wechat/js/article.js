var cur_mention_idx = 0;
var results = {};
var wrong_spans = {};

function hideClass(className) {
    var x = document.getElementsByClassName(className);
    var i;
    for (i = 0; i < x.length; ++i) {
        x[i].style.display = "none";
    }
}

function mentionClicked(mention_idx, mention_id) {
//    alert(cur_mention_idx);
    cur_mention_idx = mention_idx;
    if (cur_mention_idx + 1 == $('.span-mention').length) {
        $('#btn-submit').css({'background-color': '#337ab7', 'color': '#fff'});
    }

    $('.div-candidates').css({"display": "none"});
    //hideClass("div-main-label");
    $('.span-mention').css({"background-color": "powderblue"});
    $('.span-mention-labeled').css({"background-color": "lightgreen"});
//    span_id = "#mention-span-" + cur_mention_idx.toString();
    span_id = "#mention-span-" + mention_id;
//    alert(span_id);
    $(span_id).css({"background-color": "#FFFF55"});
    $('#div-mention-' + (cur_mention_idx + 1)).css({"display": "block"});
//    document.getElementById('div-mention-' + mention_idx).style.display='block';
}

function showSearchResult(mention_id, search_url, csrf_token) {
    postdata = {
        csrfmiddlewaretoken: csrf_token,
        mention_id: mention_id,
//        reviewed_biz_city: reviewed_biz_city,
        query_str: document.getElementById('input-query-str-' + mention_id).value,
    };

    divid = "#search-results-" + mention_id;
    $(divid).empty().load(search_url, postdata);
}

function checkRadio(mention_id, account_id, btn_id) {
    link_radio_id = 'radio-link-' + mention_id;
    document.getElementById(link_radio_id).checked = true;
    document.getElementById(btn_id).checked = true;
//    $('#div-link-' + mention_id).css({"opacity": "1"});
    results[mention_id] = account_id;

    resultStr = getResultStr();
    console.log(resultStr);
    window.parent.postMessage(resultStr, '*');
}

function linkChecked(mention_id) {
    qstr = 'input[name=link-label-' + mention_id + ']:checked'
    var checkedCandidate = $(qstr);
    if (checkedCandidate.length == 0) {
        checkRadio(mention_id, 'radio-gen-' + mention_id + '-1')
    }
}

function nolinkChecked(mention_id) {
    results[mention_id] = 'NIL';

    resultStr = getResultStr();
    console.log(resultStr);
    window.parent.postMessage(resultStr, '*');
}

function notsureChecked(mention_id) {
    results[mention_id] = 'NOS';

    resultStr = getResultStr();
    console.log(resultStr);
    window.parent.postMessage(resultStr, '*');
}

function prevMention() {
    --cur_mention_idx;
    span_id = "#mention-span-" + cur_mention_idx.toString();
    if ($(span_id).length) {
        $(span_id).trigger('click');
    } else {
        ++cur_mention_idx;
    }
}

function nextMention() {
    ++cur_mention_idx;
    span_id = "#mention-span-" + cur_mention_idx.toString();
    if ($(span_id).length) {
        $(span_id).trigger('click');
    } else {
        --cur_mention_idx;
    }
}

function getResultStr() {
    rs = '';
    for (k in results) {
        rs += k + ' ' + results[k] + ';'
    }
    for (k in wrong_spans) {
        if (wrong_spans[k]) {
            rs += k + ' WS;'
        }
    }
    return rs;
}

$(document).ready(function(){
    if ($('.span-mention').length == 1) {
        $('#btn-submit').css({'background-color': '#337ab7', 'color': '#fff'});
    }

    $('#div-mention-1').css({"display": "block"});

    $('#form-main').on('keyup keypress', function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode === 13) {
        e.preventDefault();
        return false;
        }
    });

    $('.input-search-account').on('keyup', function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode === 13) {
            var btnid = "#btn-search-" + $(this).attr('id').substring(16);
            $(btnid).trigger('click');
            return false;
        }
    });

    $('.span-mention').each(function(index) {
        mention_id = $(this).attr('id').substring(13);
        results[mention_id] = 'NIL';
        wrong_spans[mention_id] = false;
    });

    $('.checkbox-wrongspan').click(function(e) {
        mention_id = $(this).attr('name').substring(10);
        wrong_spans[mention_id] = $(this).is(':checked');

        resultStr = getResultStr();
        console.log(resultStr);
        window.parent.postMessage(resultStr, '*');
    });

    resultStr = getResultStr();
    console.log(resultStr);
    window.parent.postMessage(resultStr, '*');
});
