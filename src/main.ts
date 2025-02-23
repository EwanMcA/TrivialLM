import './style.css'

class MainPage extends HTMLElement {
  constructor() {
    super();
    this.innerHTML = `
      <form class="multi">
        <label for="genres">Genres</label>
        <select name="genres" id="genres" multiple>
          <option value="Art">Art</option>
          <option value="Entertainment">Entertainment</option>
          <option value="Food">Food</option>
          <option value="General Knowledge">General Knowledge</option>
          <option value="Geography">Geography</option>
          <option value="History">History</option>
          <option value="Science & Nature">Science & Nature</option>
          <option value="Sports">Sports</option>
        </select>
        <select name="regions" id="regions" multiple>
          <option value="Africa">Africa</option>
          <option value="Asia">Asia</option>
          <option value="Europe">Europe</option>
          <option value="North America">North America</option>
          <option value="South America">South America</option>
          <option value="Pacific">Pacific</option>
        </select>
        <button hx-post="/generate-trivia" hx-target="#trivia-questions" hx-swap="innerHTML">Generate Trivia</button>
      </form>
      <div id="trivia-questions"></div>
    `;
  }
}

customElements.define('main-page', MainPage);
