document.getElementById('fav-btn').onclick = function() {
    this.classList.toggle('active');

    let url = window.location.toString().split('/');

    if (this.classList.contains('active')) {
        httpPostAsync('/api/heart-post', function(){}, {'post_id': url[url.length - 1]});
    } else {
        httpPostAsync('/api/unheart-post', function(){}, {'post_id': url[url.length - 1]});
    }
};
