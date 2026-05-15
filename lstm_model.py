import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input 

def train_lstm(df, lookback=60):
    
    # FIX: Ensure we have enough data for the 80% train split
    train_size = int(len(df) * 0.8)
    if train_size < lookback:
        return None, None   

    data = df[['Close']].values

    scaler = MinMaxScaler()
    
    # FIX: Scaler ONLY looks at past data, then transforms everything
    scaler.fit(data[:train_size])
    scaled_data = scaler.transform(data)

    X = []
    y = []

    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i])
        y.append(scaled_data[i])

    # Keras 3 BUG FIX: Force the data to be float32 instead of float64
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    if len(X) == 0:
        return None, None   

    model = Sequential()
    
    # Keras 3 BUG FIX: Use an explicit Input layer instead of input_shape argument
    model.add(Input(shape=(lookback, 1)))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    
    # Train the model
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    return model, scaler


def predict_next(model, scaler, df, lookback=60):

    if model is None or scaler is None:
        return None   

    data = df[['Close']].values
    scaled_data = scaler.transform(data)

    # Use dynamic lookback
    last_window = scaled_data[-lookback:]
    last_window = last_window.reshape(1, lookback, 1)
    
    # Keras 3 BUG FIX: Force prediction input to float32
    last_window = np.array(last_window, dtype=np.float32)

    pred = model.predict(last_window)
    pred_price = scaler.inverse_transform(pred)

    # Safely cast the NumPy array output to a standard float
    return float(pred_price)