import frontend


if __name__ == '__main__':
    print(
        frontend.dump(
            frontend.parse(
                'assets/example.kiwi', updateGrammar=True
            )
        )
    )

