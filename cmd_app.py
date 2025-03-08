# -*- coding: gbk -*-
# 引入模块
import folder_operations as fp
import text_encoding as tcoding
import config_setting as cs
import encryption as enc

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Perform image steganography or extraction")
        print("2. Modify configuration parameters")
        print("3. Manage images in folders")
        print("4. Encode or decode text")
        print("5. Exit")
        
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            option = input("Enter '1' for steganography or '2' for extraction: ").strip()
            if option in ['1', '2']:
                enc.encryption_main(option)
            else:
                print("Invalid option.")
        elif choice == '2':
            cs.setting_main()
        elif choice == '3':
            fp.manage_folder_images()
        elif choice == '4':
            tcoding.text_coding_main()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

        continue_choice = input("\nDo you want to continue? (yes/no): ").strip().lower()
        if continue_choice != 'yes':
            print("Exiting...")
            break

if __name__ == "__main__":
    main_menu()