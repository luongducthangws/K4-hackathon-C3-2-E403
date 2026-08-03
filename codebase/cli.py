import sys
import uuid
from langchain_core.messages import HumanMessage
from backend.graph import app

def main():
    print("=" * 50)
    print("Chào mừng đến với VLearn Tutor (LangGraph Version)!")
    print("=" * 50)
    
    lecture_id = input("Nhập mã bài giảng (VD: day01, day02) [Enter để chọn 'day01']: ").strip()
    if not lecture_id:
        lecture_id = "day01"
        
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n[Đã kết nối với bài giảng '{lecture_id}'. Nhập 'quit' hoặc 'exit' để thoát]")
    
    while True:
        try:
            user_input = input("\nBạn: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Tạm biệt!")
            break
            
        if not user_input:
            continue
            
        print("Bot: ", end="", flush=True)
        
        # Gọi luồng LangGraph với chế độ stream messages
        try:
            generated_anything = False
            for chunk, metadata in app.stream(
                {"messages": [HumanMessage(content=user_input)], "lecture_id": lecture_id},
                config=config,
                stream_mode="messages"
            ):
                node = metadata.get("langgraph_node")
                # Chỉ stream những tin nhắn sinh ra từ node 'generate'
                if node == "generate":
                    generated_anything = True
                    if hasattr(chunk, "content"):
                        if isinstance(chunk.content, list):
                            text_part = "".join([item.get("text", "") for item in chunk.content if isinstance(item, dict) and "text" in item])
                            print(text_part, end="", flush=True)
                        else:
                            print(chunk.content, end="", flush=True)
                            
            # Nếu luồng bị ngắt ở evaluate (không chạy tới generate), in ra tin nhắn từ chối
            if not generated_anything:
                final_state = app.get_state(config)
                print(final_state.values["messages"][-1].content, end="")
                
            print()
            
        except Exception as e:
            print(f"\n[Lỗi kết nối: {e}]")

if __name__ == "__main__":
    main()
