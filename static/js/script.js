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

function add_required (id_name) {
    const doc = document.getElementById(id_name);
    console.log(doc);
    doc.required;
};

function remove_required (id_name) {
    document.getElementById(id_name).required = false;
}

// ラジオボタン（のみ）

function on_radio() {
    let id_select = document.getElementById('id_select_0');
    if (id_select.checked) {
//        自分で入力
        hidden_par('id_bank');
        hidden_par('id_bank_rate');
        remove_required('id_bank');
        remove_required('id_bank_rate');
        no_hidden_par('id_interest');
        add_required('id_interest');

    } else {
//        金融機関から選択
        hidden_par('id_interest');
        hidden_par('id_bank_rate');
        remove_required('id_interest')
        no_hidden_par('id_bank');
        add_required('id_bank_rate')
        select_da(interest_ra);
    };
}


function select_da(interest_ra) {
    const sel = document.getElementById('id_bank').value;
    select_bank(interest_ra);
};


// 金利タイプの選択
function select_bank (interest_ra) {
    no_hidden_par('id_bank_rate')
    remove_chi('id_bank_rate');
    let name = document.getElementById('id_bank').value;
    let bank = info.find((v) => v.bank_id === name);
    let option
    console.log(interest_ra)
    if (interest_ra) {
        interest_ra = parseFloat(interest_ra)
        option += `<option value="${interest_ra}" selected="">${interest_ra}%</option>`
    } else {

    };
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
};
