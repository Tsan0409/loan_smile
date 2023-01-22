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
    document.getElementById(id_name).classList.remove('hidden');
};


// require

function add_required (id_name) {
    const target = document.getElementById(id_name);
    target.required = true;
};

function remove_required (id_name) {
    const target = document.getElementById(id_name);
    target.required = false;
}

//min 属性
function add_min(id_name){
    console.log('add')
    const target = document.getElementById(id_name);
    target.setAttribute('min', 0.01);
};

function remove_min(id_name) {
    console.log('remove')
    const target = document.getElementById(id_name);
    target.removeAttribute('min');
};





// ラジオボタン（のみ）

function on_radio() {
    let id_select = document.getElementById('id_select_0');
    if (id_select.checked) {
//        自分で入力
        hidden_par('id_bank');
        hidden_par('id_bank_rate');
        hidden_par('id_bank_option')
        remove_required('id_bank');
        remove_required('id_bank_rate');
        no_hidden_par('id_interest');
        add_min('id_interest')
        add_required('id_interest');
    } else {
//        金融機関から選択
        remove_min('id_interest')
        hidden_par('id_interest');
        hidden_par('id_bank_rate');
        hidden_par('id_bank_option')
        remove_required('id_interest')
        no_hidden_par('id_bank');
        add_required('id_bank_rate')
        select_da(interest_ra);
    };
}


function select_da(interest_ra) {
    const page_type = 'calc';
    select_option(page_type);
    select_bank(interest_ra);
};


// 金利タイプの選択
function select_bank (interest_ra) {
    remove_chi('id_bank_rate');
    let name = Number(document.getElementById('id_bank').value);
    let bank = info.find( v => v.bank_id === name);
    let option;
    if (interest_ra > 0) {
        no_hidden_par('id_bank_rate')
        no_hidden_par('id_bank_option')
        interest_ra = parseFloat(interest_ra)
        option += `<option value="${interest_ra}" selected="">${interest_ra}%</option>`
    } else if (name === 0) {
    } else {
        no_hidden_par('id_bank_rate')
        no_hidden_par('id_bank_option')
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


// オプションタイプの選択
function select_option (page_type) {
    remove_chi('id_bank_option');
    let name = Number(document.getElementById('id_bank').value);
    let bank_option = opt.filter( v => v.bank_id === name);
    let option;
    if (bank_option.length === 0) {
        option += `<option value="0"> オプション無し </option>`;
        option += `<option value="0"> オプションは未登録です。 </option>`;
    } else {
        if (page_type === 'change') {
            option += `<option value=""> --------- </option>`;
            for (let i in bank_option ){
                if ( i === 'bank_name' | bank_option[i] === 0 ){
                } else {
                    option += `<option value="${bank_option[i]['option_id']}">${ bank_option[i]['option_name'] } : ${ bank_option[i]['option_rate'] }%</option>`;
                };
            };
        } else {
            if (option_return == false || option_return === '0') {
                option += `<option value="0"> オプション無し </option>`
            } else {
                option += `<option value="${option_return}">${option_return}%</option>`
                option += `<option value="0"> オプション無し </option>`
            };
            for (let i in bank_option ){
                if ( i === 'bank_name' | bank_option[i] === 0 ){
                } else {
                    option += `<option value="${bank_option[i]['option_rate']}">${ bank_option[i]['option_name'] } : ${ bank_option[i]['option_rate'] }%</option>`;
                };
            };
        };
    };
    document.getElementById('id_bank_option').insertAdjacentHTML('afterbegin', option);
};

//金利の0以下が入力されている場合削除する
function errorCheck() {
    console.log('start: error check')
	var interest = document.getElementById('id_interest');
  if ( interest.value <= 0  ) {
  	interest.value = '';
  }
}
