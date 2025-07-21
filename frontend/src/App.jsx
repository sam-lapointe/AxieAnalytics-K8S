import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Home } from "./pages/home.jsx"
import { Axies } from "./pages/axies.jsx"
import { Layout } from "./pages/layout.jsx"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />}/>
          <Route path="axies/*" element={<Axies />} />
          <Route path="*" element={<Home />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
