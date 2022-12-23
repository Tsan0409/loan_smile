'use strict';


// 子要素全て消去(引数は文字列で)
function remove_chi(parent_id) {
    let parent = document.getElementById(parent_id);
    while(parent.lastChild){
        parent.removeChild(parent.lastChild);
    }
};

// 祖父要素を隠す

function hidden_par(base_id) {
    document.getElementById(base_id).parentNode.parentNode.classList.add('hidden');
};

function no_hidden_par(base_id) {
    document.getElementById(base_id).parentNode.parentNode.classList.remove('hidden');
};

// 要素を隠す（class=hidden)
function hidden(id_name) {
    document.getElementById(id_name).classList.add('hidden');
};

// 隠した要素を戻す（class=hidden)
function no_hidden(id_name) {
    console.log('no_hidden')
    document.getElementById(id_name).classList.remove('hidden');
};

// 要素消す


// ラジオボタン（のみ）

function on_radio() {
    let id_select = document.getElementById('id_select_0');
    if (id_select.checked) {
        hidden_par('id_bank')
        hidden_par('id_bank_rate')
        no_hidden_par('id_interest')
    } else {
        hidden_par('id_interest')
        hidden_par('id_bank_rate')
        no_hidden_par('id_bank')

    }
}


function select_da() {
    const sel = document.getElementById('id_bank').value;
    select_bank();
};


// 金利タイプの選択
function select_bank () {
    no_hidden_par('id_bank_rate')
    remove_chi('id_bank_rate');
    let name = document.getElementById('id_bank').value;
    let bank = info.find((v) => v.bank_id === name);
    let option = `<option value="" selected="">---------</option>`
    for ( let n in order) {
        for (let i in bank ){
            if ( i === 'bank_name' | bank[i] === 0 ){
            } else if( order[n] === i ) {
                option += `<option value="${bank[i]}"> ${ i }：${ bank[i] }%</option>`;
            } else {
            };
        };
    };
    document.getElementById('id_bank_rate').insertAdjacentHTML('afterbegin', option);
    }
