import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Suppliers from './pages/Suppliers'
import Home from './pages/Home'
import ProductSearch from './components/ProductSearch'
import Sidebar from './components/Navbar'


//<a target="_blank" href="https://icons8.com/icon/3439/about">About</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>

const App = () => {
  return (
    <div className='bg-[#F8F9FD]'>
      <div className='flex items-start'>
      <Sidebar/>
      <div className="flex-1 p-5">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/suppliers" element={<Suppliers />} />
        <Route path="/search" element={<ProductSearch />} />
      </Routes>
      </div>
      </div>
    </div>
  )
}

export default App