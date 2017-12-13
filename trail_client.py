import grpc

import trail_pb2
import trail_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50052')
    stub = trail_pb2_grpc.TrailStub(channel)
    data = '[{"name": "x", "value": 0.54881350392732475}, {"name": "y", "value": 0.71518936637241948}]'
    trail_id = 1
    response = stub.RunTrail(trail_pb2.Data(data=data, trail_id=trail_id))
    print(response.message)

if __name__ == "__main__":
    run()
