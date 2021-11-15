function get_cur_slide() {
    let idx = window.location.hash.substr(1);
    if (idx == '') {
        idx = '1';
    }
    return Number(idx);
}

function set_cur_slide(idx) {
    window.location.hash = idx;
}

function update() {
    let cur_slide_idx = get_cur_slide();
    let all_slides = document.querySelectorAll('svg[data-slimd-svg=""]');
    let cur_slide = document.getElementById('slide-' + cur_slide_idx);

    all_slides.forEach(s => {
        if (s === cur_slide) {
            s.classList.add('slimd-active');
        } else {
            s.classList.remove('slimd-active');
        }
    })
}

document.querySelectorAll('.katex').forEach(e => {
    let o = MathJax.tex2svg(e.innerHTML, {
        display: e.classList.contains('katex-display')
    });
    e.innerHTML = o.innerHTML;
})

document.body.onkeydown = (ev) => {
    let cur_idx = get_cur_slide();
    if (ev.keyCode == 37 || ev.keyCode == 38 || ev.keyCode == 33) {
        if (cur_idx > 1) {
            set_cur_slide(cur_idx - 1);
            update();
        }
    }

    if (ev.keyCode == 39 || ev.keyCode == 40 || ev.keyCode == 34) {
        if (cur_idx < SLIMD_MAX_SLIDE) {
            set_cur_slide(cur_idx + 1);
            update();
        }
    }
}

update();