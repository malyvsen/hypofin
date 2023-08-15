import { Link } from "react-router-dom";

function LandingPage() {
  return (
    <div className="Page">
      <h1>Kalkulator oszczędności</h1>
      <p>
        Co robić z oszczędnościami? Na to pytanie musisz znaleźć własną
        odpowiedź, ale ten kalkulator pomoże ci szybko przeanalizować wiele
        możliwości.
      </p>
      <Link to="/situation">Zaczynajmy!</Link>
    </div>
  );
}

export default LandingPage;
