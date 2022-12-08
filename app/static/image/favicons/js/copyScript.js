const copyBtn = document.querySelector('#copy-pre')

copyBtn.onclick = () => {
    const preContent = document.querySelector('#pre-for-copy').innerHTML

    navigator.clipboard.writeText(preContent)
    .then(() => {})
    .catch(err => {
        aletr('Sometrhing went wrong', err)
    })
}