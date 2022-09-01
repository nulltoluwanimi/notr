
// note-home
const modal = document.getElementById('label_modal');
const continueBtn = document.getElementById('continueBtn');
const commentSection = document.getElementById('commentSection');
const label_section = document.getElementById('label_section');

//edit-profile
const password = document.getElementById('password_modal');
const change_password = document.getElementById('password_btn');
const password_section = document.getElementById('label_section');

const logout = document.getElementById('popup-modal');
const logout_button = document.getElementById('logout_btn');

const edit = document.getElementById('edit_btn');

const notes_info = document.querySelector('#notes-info');
const edit_modal = document.querySelectorAll('#edit-action');

const delete_btn = document.getElementById('delete_btn');
const delete_modal = document.querySelector('#delete-modal');
// const delete_div = document.getElementById('delete')

const comment_btn = document.getElementById('comment_btn');
const comment_section = document.getElementById('comment-section');
const comment_modal = document.getElementById('comment-modal');

const share_btn = document.getElementById('share_btn');
const share_modal = document.getElementById('share_modal');
const share_section = document.getElementById('share_section');


share_btn?.addEventListener('click', () => {
  share_section.style.display = 'flex'
  share_modal.style.display = 'flex'
})

share_modal?.addEventListener('click', (e) => {
  if (e.target.id === 'share_modal') {
    share_modal.style.display = 'none';
  }
})

comment_btn?.addEventListener('click', () => {
  comment_section.style.display = 'block';
  comment_modal.style.display = 'flex';
});

comment_modal?.addEventListener('click', (e) => {
  if (e.target.id === 'comment_modal') {
    comment_modal.style.display = 'none';
  }
})

function close_dialog_comment() {
  comment_modal.style.display = "none"

}
edit?.addEventListener('click', () => {
  edit_modal.forEach((element) => {
    element.style.display = 'flex';
  })
});

delete_btn?.addEventListener('click', () => {
  // delete_modal.forEach((element) => {
  // console.log(element)
  delete_modal.style.display = 'flex';
  // });
});

function closeDialogtrash() {
  delete_modal.style.display = "none"
}

logout_button?.addEventListener('click', () => {
  logout.style.display = 'flex';
});

function closeDialog() {
  logout.style.display = "none"

}

logout?.addEventListener('click', (e) => {
  if (e.target.id === 'popup-modal') {
    logout.style.display = 'none';
  }
});


change_password?.addEventListener('click', () => {
  password.style.display = 'flex';
  password_section.style.display = 'flex';
});

continueBtn?.addEventListener('click', () => {
  label_section.style.display = 'flex';
  modal.style.display = 'flex';
});
const commentBtn = document.getElementById('commentBtn');
commentBtn?.addEventListener('click', () => {
  commentSection.style.display = 'block';
  modal.style.display = 'flex';
});
modal?.addEventListener('click', (e) => {
  if (e.target.id === 'label_modal') {
    modal.style.display = 'none';
  }
});


document?.getElementById("cp_btn")?.addEventListener("click", CopyText);

var copyText = document?.getElementById("link");

// copyText.onclick = function () {
//   document.execCommand("copy");
// }

// copyText.addEventListener("copy", function (event) {
//   event.preventDefault();
//   if (event.clipboardData) {
//     event.clipboardData.setData("text/plain", span.textContent);
//   }
// });



