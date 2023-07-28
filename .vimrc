call plug#begin()

Plug 'preservim/nerdtree'
Plug 'vim-airline/vim-airline'

call plug#end()


autocmd FileType python map <buffer> <F9> :w<CR>:exec '!python3' shellescape(@%, 1)<CR>
autocmd FileType python imap <buffer> <F9> <esc>:w<CR>:exec '!python3' shellescape(@%, 1)<CR>
autocmd VimEnter * NERDTree


set tabstop=4
set shiftwidth=4
set rnu
set nu
set redrawtime=5000
set autoread

