import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import MatcherPage from './pages/MatcherPage'
import ResultsPage from './pages/ResultsPage'
import HistoryPage from './pages/HistoryPage'
import AboutPage from './pages/AboutPage'
import ResumeOptimization from './pages/ResumeOptimization'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/matcher" element={<MatcherPage />} />
            <Route path="/results/:id" element={<ResultsPage />} />
            <Route path="/optimize/:id" element={<ResumeOptimization />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}
