import { useState, useEffect, useRef } from 'react';
import './App.css';  // We'll create this next

export default function SMSSender() {
  const [tab, setTab] = useState('send');
  const [scannedCode, setScannedCode] = useState('');
  const [message, setMessage] = useState('');
  const [messageHistory, setMessageHistory] = useState([]);
  const [mappings, setMappings] = useState({});
  const [newCode, setNewCode] = useState('');
  const [newPhone, setNewPhone] = useState('+1');
  const inputRef = useRef(null);

  useEffect(() => {
    fetchMappings();
  }, []);

  const fetchMappings = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/mappings');
      const data = await response.json();
      setMappings(data);
    } catch (error) {
      console.error('Error fetching mappings:', error);
    }
  };

  const handleCodeInput = async (e) => {
    const value = e.target.value;
    setScannedCode(value);
    
    if (value.length === 6) {
      try {
        const response = await fetch('http://localhost:5000/api/send-message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code: value,
            message: message,
          }),
        });
        
        const data = await response.json();
        if (response.ok) {
          setMessageHistory(prev => [{
            timestamp: new Date().toLocaleString(),
            code: value,
            phoneNumber: data.phone,
            message: message,
            status: 'Sent'
          }, ...prev]);
          setScannedCode('');
          e.target.value = '';
        } else {
          alert(data.error || 'Failed to send message');
        }
      } catch (error) {
        console.error('Error sending message:', error);
        alert('Error sending message');
      }
    }
  };

  const addMapping = async () => {
    if (newCode.length !== 6) {
      alert('Code must be 6 digits');
      return;
    }
    if (!newPhone) {
      alert('Please enter a phone number');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/mapping', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: newCode,
          phone: newPhone,
        }),
      });
      
      if (response.ok) {
        setMappings(prev => ({
          ...prev,
          [newCode]: newPhone
        }));
        setNewCode('');
        setNewPhone('+1');
      }
    } catch (error) {
      console.error('Error adding mapping:', error);
      alert('Error adding mapping');
    }
  };

  useEffect(() => {
    if (tab === 'send') {
      inputRef.current?.focus();
    }
  }, [tab]);

  return (
    <div className="app">
      <div className="container">
        <div className="tabs">
          <button 
            className={`tab ${tab === 'send' ? 'active' : ''}`}
            onClick={() => setTab('send')}
          >
            Send SMS
          </button>
          <button 
            className={`tab ${tab === 'mappings' ? 'active' : ''}`}
            onClick={() => setTab('mappings')}
          >
            Number Mappings
          </button>
          <button 
            className={`tab ${tab === 'history' ? 'active' : ''}`}
            onClick={() => setTab('history')}
          >
            History
          </button>
        </div>

        <div className="content">
          {tab === 'send' && (
            <div className="section">
              <h2>Scan Barcode</h2>
              <div className="input-group">
                <label>Scan 6-Digit Code</label>
                <input
                  ref={inputRef}
                  type="text"
                  maxLength={6}
                  onChange={handleCodeInput}
                  placeholder="Scanner will input code here..."
                />
              </div>
              <div className="input-group">
                <label>Message Template</label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
          )}

          {tab === 'mappings' && (
            <div className="section">
              <h2>Code to Phone Number Mappings</h2>
              <div className="mapping-form">
                <div className="input-group">
                  <label>6-Digit Code</label>
                  <input
                    type="text"
                    maxLength={6}
                    value={newCode}
                    onChange={(e) => setNewCode(e.target.value)}
                    placeholder="Enter 6-digit code"
                  />
                </div>
                <div className="input-group">
                  <label>Phone Number</label>
                  <input
                    type="text"
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
                <button onClick={addMapping} className="add-button">
                  Add Mapping
                </button>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Phone Number</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(mappings).map(([code, phone]) => (
                    <tr key={code}>
                      <td>{code}</td>
                      <td>{phone}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'history' && (
            <div className="section">
              <h2>Message History</h2>
              <table>
                <thead>
                  <tr>
                    <th>Time Sent</th>
                    <th>Code</th>
                    <th>Phone Number</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {messageHistory.map((msg, i) => (
                    <tr key={i}>
                      <td>{msg.timestamp}</td>
                      <td>{msg.code}</td>
                      <td>{msg.phoneNumber}</td>
                      <td>{msg.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}