'use strict';




// 子要素全て消去(引数は文字列で)
function remove_chi(parent_id) {
    let parent = document.getElementById(parent_id);
    while(parent.lastChild){
        parent.removeChild(parent.lastChild);
    }
};

// 要素を隠す（class=hidden)

function hidden(id_name) {
    document.getElementById(id_name).classList.add('hidden');
}


// 要素消す


// ラジオボタン（のみ）



// フォーム分岐
function check_radiobutton(radio_btn, name){
    if ( radio_btn === 0 ) {
        document.getElementById('input_radio').checked = true;
        select_input();
    } else if ( radio_btn === 1 ) {
        document.getElementById('select_radio').checked = true;
        select_select()
        document.querySelector(`option[value="${name}"]`).selected = true;
        select_bank()
    } else {
        hidden('ans')
        document.getElementById('input_radio').checked = true;
        select_input()
    }}


// 自ら入力
function select_input() {
    remove_chi('insert_form');
    const form = `<input class="form-text" type="number" value="${rate}" id="interest_rate" name="interest_rate" placeholder="2.475" min="0.001" step="0.001">% `;
    document.getElementById('insert_form').insertAdjacentHTML('beforeend', form);
}

// 金融機関の選択
function select_select() {
    let bank = [] ;
    let select = `<select name="bank_name" id="bank_name" class="form-text" onchange="select_bank()" required><option value=""> 選択してください </option> `;
    for (let n in info) {
        bank.push(info[n].bank_name)
    }
    remove_chi('insert_form');
    for ( let i in bank ) {
        select += `<option name="${bank[i]}" value="${bank[i]}"> ${ bank[i]}</option>`
    }
    select += '</select><br><br><span id="insert_rate"></span>';
    document.getElementById('insert_form').insertAdjacentHTML('beforeend', select);
};


// 金利タイプの選択
function select_bank () {
    remove_chi('insert_rate');
    let name = document.getElementById('bank_name').value;
    let bank = info.find((v) => v.bank_name === name);
    let option = '<select class="form-text" name="bank_rate" id="bank_rate" required >%';
    for ( let n in order) {
        for (let i in bank ){
            if ( i === 'bank_name' | bank[i] === 0 ){
            } else if( order[n] === i ) {
                option += `<option value="${bank[i]}"> ${ i }：${ bank[i] }%</option>`;
            } else {
            };
        };
    };
    option += '</select>';
    document.getElementById('insert_rate').insertAdjacentHTML('beforeend', option);
    }
