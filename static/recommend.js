$(function() {
  // Button will be disabled until we type anything inside the input field
  const source = document.getElementById('autoComplete');
  const source1 = document.getElementById('autoComplete1');
  // const hidekaro=document.querySelector('.input-container');
  const inputHandler = function(e) {
    if(e.target.value==""){
      $('.movie-button').attr('disabled', true);
    }
    else{
      const inputHandler1 = function(e) {
    if(e.target.value==""){
      $('.movie-button').attr('disabled', true);
    }
    else{
      
      $('.movie-button').attr('disabled', false);
    }
  }
      source1.addEventListener('input', inputHandler1);
    }
  }
  source.addEventListener('input', inputHandler);
  $('.movie-button').on('click',function(){
    // hidekaro.style.display="none";
    var my_api_key = '04b9df5416d75be096abd805b24b47a1';
    var title = $('.movie').val();
    console.log(title);
    var lang=$('#autoComplete1').val();
    // console.log(Lang);
    lang=lang.toLowerCase();
    if(lang=="en")
      lang='en';
    else if(lang=="hi")
      lang='hi';
    else
    {
      alert("Please Enter en or hi only");
      $('#autoComplete').val('');
      $('#autoComplete1').val('');
      windows.navigate("index.html");
    }
    if (title=="") {
      $('.results').css('display','none');
      $('.fail').css('display','block');
    }
    else{
      load_details(my_api_key,title,lang);
    }
  });
});

// will be invoked when clicking on the recommended movies
function recommendcard(e){
  var my_api_key = '04b9df5416d75be096abd805b24b47a1';
  var title = e.getAttribute('title');
  console.log(title)
  load_details(my_api_key,title);
}

// get the basic details of the movie from the API (based on the name of the movie)
function load_details(my_api_key,title,lang){
  
  $.ajax({
    type: 'GET',
    url:'https://api.themoviedb.org/3/discover/movie?api_key='+my_api_key+'&with_text_query='+title+'&with_original_language='+lang,
    async: false,
    success: function(movie){
      if(movie.results.length<1){
        $('.fail').css('display','block');
        $('.results').css('display','none');
        $("#loader").delay(500).fadeOut();
      }
      else if(movie.results.length==1) {
        $("#loader").fadeIn();
        $('.fail').css('display','none');
        $('.results').delay(1000).css('display','block');
        var movie_id = movie.results[0].id;
        var movie_title = movie.results[0].title;
        var movie_title_org = movie.results[0].original_title;
        movie_recs(movie_title,movie_id,my_api_key);
      }
      else{
        var close_match = {};
        var flag=0;
        var movie_id="";
        var movie_title="";
        var movie_title_org="";
        $("#loader").fadeIn();
        $('.fail').css('display','none');
        $('.results').delay(1000).css('display','block');
        for(var count in movie.results){
          if(title==movie.results[count].title){
            flag = 1;
            movie_id = movie.results[count].id;
            movie_title = movie.results[count].title;
            movie_title_org = movie.results[count].original_title;
            break;
          }
          else{
            close_match[movie.results[count].title] = similarity(title,  movie.results[count].title);
          }
        }
        if(flag==0){
          movie_title = Object.keys(close_match).reduce(function(a, b){ return close_match[a] > close_match[b] ? a : b });
          var index = Object.keys(close_match).indexOf(movie_title)
          movie_id = movie.results[index].id;
          movie_title_org = movie.results[index].original_title;
        }
        console.log(movie_title);
        console.log(movie_id)
        movie_recs(movie_title,movie_id,my_api_key);
      }
    },
    error: function(error){
      alert('Invalid Request - '+error);
      $("#loader").delay(500).fadeOut();
    },
  });
}
function similarity(s1, s2) {
  var longer = s1;
  var shorter = s2;
  if (s1.length < s2.length) {
    longer = s2;
    shorter = s1;
  }
  var longerLength = longer.length;
  if (longerLength == 0) {
    return 1.0;
  }
  return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
}

function editDistance(s1, s2) {
  s1 = s1.toLowerCase();
  s2 = s2.toLowerCase();

  var costs = new Array();
  for (var i = 0; i <= s1.length; i++) {
    var lastValue = i;
    for (var j = 0; j <= s2.length; j++) {
      if (i == 0)
        costs[j] = j;
      else {
        if (j > 0) {
          var newValue = costs[j - 1];
          if (s1.charAt(i - 1) != s2.charAt(j - 1))
            newValue = Math.min(Math.min(newValue, lastValue),
              costs[j]) + 1;
          costs[j - 1] = lastValue;
          lastValue = newValue;
        }
      }
    }
    if (i > 0)
      costs[s2.length] = lastValue;
  }
  return costs[s2.length];
}
// passing the movie name to get the similar movies from python's flask
function movie_recs(movie_title,movie_id,my_api_key){
  console.log(movie_title);
  $.ajax({
    type:'POST',
    url:"/similarity",
    data:{'name':movie_title},
    success: function(recs){
      if(recs=="Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies"){
        $('.fail').css('display','block');
        $('.results').css('display','none');
        $("#loader").delay(500).fadeOut();
      }
      else {
        $('.fail').css('display','none');
        $('.results').css('display','block');
        var movie_arr = recs.split('---');
        var arr = [];
        for(const movie in movie_arr){
          arr.push(movie_arr[movie]);
          // console.log(movie_arr[movie])
        }
        get_movie_details(movie_id,my_api_key,arr,movie_title);
      }
    },
    error: function(){
      console.log(movie_title)
      alert("Movie Does Not Exist In The Database");
      $("#loader").delay(500).fadeOut();
    },
  }); 
}

// get all the details of the movie using the movie id.
function get_movie_details(movie_id,my_api_key,arr,movie_title) {
  $.ajax({
    type:'GET',
    url:'https://api.themoviedb.org/3/movie/'+movie_id+'?api_key='+my_api_key,
    success: function(movie_details){
      show_details(movie_details,arr,movie_title,my_api_key,movie_id);
    },
    error: function(){
      alert("API Error!");
      $("#loader").delay(500).fadeOut();
    },
  });
}

// passing all the details to python's flask for displaying and scraping the movie reviews using imdb id
function show_details(movie_details,arr,movie_title,my_api_key,movie_id){
  var imdb_id = movie_details.imdb_id;
  var poster = 'https://image.tmdb.org/t/p/original'+movie_details.poster_path;
  var overview = movie_details.overview;
  var genres = movie_details.genres;
  var rating = movie_details.vote_average;
  var vote_count = movie_details.vote_count;
  var release_date = new Date(movie_details.release_date);
  var runtime = parseInt(movie_details.runtime);
  var status = movie_details.status;
  var genre_list = []
  for (var genre in genres){
    genre_list.push(genres[genre].name);
  }
  var my_genre = genre_list.join(", ");
  if(runtime%60==0){
    runtime = Math.floor(runtime/60)+" hour(s)"
  }
  else {
    runtime = Math.floor(runtime/60)+" hour(s) "+(runtime%60)+" min(s)"
  }
  arr_poster = get_movie_posters(arr,my_api_key);
  
  movie_cast = get_movie_cast(movie_id,my_api_key);
  
  ind_cast = get_individual_cast(movie_cast,my_api_key);
  
  details = {
    'title':movie_title,
      'cast_ids':JSON.stringify(movie_cast.cast_ids),
      'cast_names':JSON.stringify(movie_cast.cast_names),
      'cast_chars':JSON.stringify(movie_cast.cast_chars),
      'cast_profiles':JSON.stringify(movie_cast.cast_profiles),
      'cast_bdays':JSON.stringify(ind_cast.cast_bdays),
      'cast_bios':JSON.stringify(ind_cast.cast_bios),
      'cast_places':JSON.stringify(ind_cast.cast_places),
      'imdb_id':imdb_id,
      'poster':poster,
      'genres':my_genre,
      'overview':overview,
      'rating':rating,
      'vote_count':vote_count.toLocaleString(),
      'release_date':release_date.toDateString().split(' ').slice(1).join(' '),
      'runtime':runtime,
      'status':status,
      'rec_movies':JSON.stringify(arr),
      'rec_posters':JSON.stringify(arr_poster),
  }

  $.ajax({
    type:'POST',
    data:details,
    url:"/recommend",
    dataType: 'html',
    complete: function(){
      $("#loader").delay(500).fadeOut();
    },
    success: function(response) {
      $('.results').html(response);
      $('#autoComplete').val('');
      $('#autoComplete1').val('');
      $(window).scrollTop(0);
    }
  });
}

// get the details of individual cast
function get_individual_cast(movie_cast,my_api_key) {
    cast_bdays = [];
    cast_bios = [];
    cast_places = [];
    for(var cast_id in movie_cast.cast_ids){
      $.ajax({
        type:'GET',
        url:'https://api.themoviedb.org/3/person/'+movie_cast.cast_ids[cast_id]+'?api_key='+my_api_key,
        async:false,
        success: function(cast_details){
          cast_bdays.push((new Date(cast_details.birthday)).toDateString().split(' ').slice(1).join(' '));
          cast_bios.push(cast_details.biography);
          cast_places.push(cast_details.place_of_birth);
        }
      });
    }
    return {cast_bdays:cast_bdays,cast_bios:cast_bios,cast_places:cast_places};
  }

// getting the details of the cast for the requested movie
function get_movie_cast(movie_id,my_api_key){
    cast_ids= [];
    cast_names = [];
    cast_chars = [];
    cast_profiles = [];

    top_10 = [0,1,2,3,4,5,6,7,8,9];
    $.ajax({
      type:'GET',
      url:"https://api.themoviedb.org/3/movie/"+movie_id+"/credits?api_key="+my_api_key,
      async:false,
      success: function(my_movie){
        if(my_movie.cast.length>=10){
          top_cast = [0,1,2,3,4,5,6,7,8,9];
        }
        else{
          top_cast=[];
          for(var i=0;i<my_movie.cast.length;i++){
            top_cast.push(i);
          }
        }
        for(var my_cast in top_cast){
          cast_ids.push(my_movie.cast[my_cast].id)
          cast_names.push(my_movie.cast[my_cast].name);
          cast_chars.push(my_movie.cast[my_cast].character);
          if (my_movie.cast[my_cast].profile_path){
            cast_profiles.push("https://image.tmdb.org/t/p/original"+my_movie.cast[my_cast].profile_path);
        }
        else{
          cast_profiles.push("../static/notfound.jpg");
        }
        }
      },
      error: function(){
        alert("Invalid Request!");
      }
    });

    return {cast_ids:cast_ids,cast_names:cast_names,cast_chars:cast_chars,cast_profiles:cast_profiles};
  }

// getting posters for all the recommended movies
function get_movie_posters(arr,my_api_key){
  var arr_poster_list = []
  for(var m in arr) {
    // console.log(arr[m]);
    $.ajax({
      type:'GET',
      url:'https://api.themoviedb.org/3/search/movie?api_key='+my_api_key+'&query='+arr[m],
      async: false,
      success: function(m_data){
        arr_poster_list.push('https://image.tmdb.org/t/p/original'+m_data.results[0].poster_path);
      },
      error: function(){
        alert("Invalid Request!");
        $("#loader").delay(500).fadeOut();
      },
    })
  }
  return arr_poster_list;
}