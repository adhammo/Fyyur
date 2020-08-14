window.parseISOString = function parseISOString(s) {
    var b = s.split(/\D+/);
    return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// Seeking
const seeking_venue = document.getElementById('seeking_venue');
const seeking_talent = document.getElementById('seeking_talent');
const seeking_description = document.getElementById('seeking_description');
if (seeking_venue) {
    if (seeking_venue.checked) seeking_description.classList.remove('hidden');
    else seeking_description.classList.add('hidden');

    seeking_venue.onchange = function (e) {
        if (e.target.checked) seeking_description.classList.remove('hidden');
        else seeking_description.classList.add('hidden');
    };
}

if (seeking_talent) {
    if (seeking_talent.checked) seeking_description.classList.remove('hidden');
    else seeking_description.classList.add('hidden');

    seeking_talent.onchange = function (e) {
        if (e.target.checked) seeking_description.classList.remove('hidden');
        else seeking_description.classList.add('hidden');
    };
}

// Available
const available_times = document.getElementById('available_times');
const available_start = document.getElementById('available_start');
const available_end = document.getElementById('available_end');
if (available_times) {
    if (available_times.checked) {
        available_start.classList.remove('hidden');
        available_end.classList.remove('hidden');
    } else {
        available_start.classList.add('hidden');
        available_end.classList.add('hidden');
    }

    available_times.onchange = function (e) {
        if (e.target.checked) {
            available_start.classList.remove('hidden');
            available_end.classList.remove('hidden');
        } else {
            available_start.classList.add('hidden');
            available_end.classList.add('hidden');
        }
    };
}

// Deletion
const deleteButtons = document.querySelectorAll('.delete');
for (let index = 0; index < deleteButtons.length; index++) {
    const deleteButton = deleteButtons[index];
    if (deleteButton) {
        deleteButton.onclick = function (e) {
            e.preventDefault();
            fetch(`/${deleteButton.dataset['name']}/${deleteButton.dataset['id']}`, { method: 'DELETE', redirect: 'manual' })
                .then(() => {
                    window.location.replace('/');
                })
                .catch(function (err) {
                    console.error(err);
                });
        };
    }
}
